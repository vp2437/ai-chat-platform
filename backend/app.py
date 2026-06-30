from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from gemini_function_calling import ask_gemini
from mcp_client import MCPManager

mcp_manager = MCPManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mcp_manager.connect_all()
    yield
    await mcp_manager.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/chat")
async def chat(data: dict):
    message = data["message"]
    tools = await mcp_manager.get_gemini_tools()
    response_text = await ask_gemini(message, tools, mcp_manager)
    return {"response": response_text}