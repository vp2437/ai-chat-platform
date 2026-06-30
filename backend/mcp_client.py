import os
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Base path to the mcp-prototypes repo, set via .env
MCP_PROTOTYPES_DIR = os.getenv("MCP_PROTOTYPES_DIR")

if not MCP_PROTOTYPES_DIR:
    raise RuntimeError(
        "MCP_PROTOTYPES_DIR is not set. Add it to your .env file, "
        "pointing to your local clone of the mcp-prototypes repo."
    )

SERVERS = {
    "excel": os.path.join(MCP_PROTOTYPES_DIR, "excel_mcp", "server.py"),
    "pdf":   os.path.join(MCP_PROTOTYPES_DIR, "pdf_mcp", "server.py"),
    "sql":   os.path.join(MCP_PROTOTYPES_DIR, "sql_mcp", "server.py"),
    "dxf":   os.path.join(MCP_PROTOTYPES_DIR, "dxf_mcp", "server.py"),
}

class MCPManager:
    def __init__(self):
        self.sessions = {}     
        self.tool_to_server = {}  
        self.exit_stack = AsyncExitStack()

    async def connect_all(self):
        for name, path in SERVERS.items():
            params = StdioServerParameters(command="python", args=[path])
            read, write = await self.exit_stack.enter_async_context(stdio_client(params))
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.sessions[name] = session

            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                self.tool_to_server[tool.name] = name

    EXCLUDED_TOOLS = {"server_directory"}

    async def get_gemini_tools(self):
        function_declarations = []
        seen_names = set()
        for session in self.sessions.values():
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                if tool.name in self.EXCLUDED_TOOLS or tool.name in seen_names:
                    continue
                seen_names.add(tool.name)
                schema = dict(tool.inputSchema) if tool.inputSchema else {"type": "object", "properties": {}}
                schema.pop("additionalProperties", None)
                schema.pop("$schema", None)
                function_declarations.append({
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": schema
                })
        return [{"function_declarations": function_declarations}]

    async def call_tool(self, tool_name, args):
        server_name = self.tool_to_server.get(tool_name)
        if not server_name:
            return f"Unknown tool {tool_name}"
        session = self.sessions[server_name]
        result = await session.call_tool(tool_name, args)
        texts = [block.text for block in result.content if hasattr(block, "text")]
        return "\n".join(texts) if texts else "(no output)"

    async def close(self):
        await self.exit_stack.aclose()