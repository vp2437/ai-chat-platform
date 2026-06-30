from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def ask_gemini(message, tools, mcp_manager, max_turns=5):
    contents = [types.Content(role="user", parts=[types.Part(text=message)])]

    for _ in range(max_turns):
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=contents,
            config={"tools": tools}
        )
        candidate = response.candidates[0]
        parts = candidate.content.parts

        function_call_part = next((p for p in parts if hasattr(p, "function_call") and p.function_call), None)

        if not function_call_part:
            return response.text

        fc = function_call_part.function_call
        tool_result = await mcp_manager.call_tool(fc.name, dict(fc.args))

        contents.append(candidate.content)
        contents.append(types.Content(
            role="user",
            parts=[types.Part(function_response=types.FunctionResponse(
                name=fc.name,
                response={"result": tool_result}
            ))]
        ))

    return "Reached max tool-call turns without a final answer."