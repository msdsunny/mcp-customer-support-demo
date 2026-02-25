import sys
import os
import json
import atexit
import signal
import subprocess
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AsyncOpenAI
import traceback

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Detect environment: if MCP_SERVER_URL is set, use REST API (Vercel mode)
# Otherwise, use stdio transport (local mode)
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "").strip()
IS_REMOTE = bool(MCP_SERVER_URL)

# -- Globals --
mcp_session = None   # Only used in local mode
openai_tools = []


def cleanup_child_processes():
    """Kill all child processes of the current Python process (Windows-compatible)."""
    current_pid = os.getpid()
    try:
        # /T = kill entire process tree, /F = force, /PID = target process
        # We kill children of THIS process, which includes the MCP server subprocess
        result = subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(current_pid)],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print(f"[Cleanup] Terminated child process tree of PID {current_pid}")
    except Exception:
        pass  # Best-effort cleanup


atexit.register(cleanup_child_processes)


def signal_handler(sig, frame):
    """Handle Ctrl+C / termination signals gracefully."""
    print("\n[Shutdown] Received termination signal, cleaning up...")
    cleanup_child_processes()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize OpenAI Client using Environment Variables
openai_client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL")
)

# Manage state for different sessions/tabs
chat_history = {}

# ============================================================
# MODE 1: Remote / Vercel  (REST API calls via httpx)
# ============================================================
async def fetch_tools_remote():
    """Fetch the list of tools from the remote MCP Server REST API."""
    global openai_tools
    if openai_tools:
        return
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MCP_SERVER_URL}/tools", timeout=10)
        response.raise_for_status()
        data = response.json()
        for tool in data["tools"]:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            })
    print(f"[Remote] Fetched {len(openai_tools)} tools: {[t['function']['name'] for t in openai_tools]}")

async def call_tool_remote(name: str, arguments: dict) -> str:
    """Call a tool on the remote MCP Server via REST API."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MCP_SERVER_URL}/call_tool",
            json={"name": name, "arguments": arguments},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("result", "No result returned")

# ============================================================
# MODE 2: Local (stdio transport via MCP SDK)
# ============================================================
@asynccontextmanager
async def local_lifespan(app: FastAPI):
    """Lifespan for local mode: spawns MCP server as a subprocess."""
    global mcp_session, openai_tools
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    # Resolve the path to server.py in the sibling mcp-server directory
    server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mcp-server", "server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env=None
    )

    print("[Local] Starting MCP connection via stdio...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            mcp_session = session
            await session.initialize()
            print("[Local] Successfully connected to MCP Server!")

            tools = await session.list_tools()
            for tool in tools.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            print(f"[Local] Discovered {len(openai_tools)} tools: {[t['function']['name'] for t in openai_tools]}")
            yield

    print("[Local] MCP connection closed.")

async def call_tool_local(name: str, arguments: dict) -> str:
    """Call a tool on the local MCP server via stdio session."""
    result = await mcp_session.call_tool(name, arguments=arguments)
    return "\n".join(content.text for content in result.content)

# ============================================================
# Setup FastAPI (choose lifespan based on mode)
# ============================================================
if IS_REMOTE:
    print(f"🌐 Running in REMOTE mode → MCP Server at {MCP_SERVER_URL}")
    app = FastAPI()  # No lifespan needed — tools fetched lazily
else:
    print("🏠 Running in LOCAL mode → MCP Server via stdio subprocess")
    app = FastAPI(lifespan=local_lifespan)

# Setup schemas
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    tools_used: list[str]

# Serve static files (conditional for Vercel compatibility)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>MCP Client</h1><p>Static files not found.</p>", status_code=500)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_msg = request.message

    # In remote mode, fetch tools lazily on first request
    if IS_REMOTE:
        await fetch_tools_remote()

    # Initialize session history if new
    if session_id not in chat_history:
        chat_history[session_id] = [
            {"role": "system", "content": "You are a helpful customer support assistant for a business. Use your tools to lookup customer info and order status when asked."}
        ]

    messages = chat_history[session_id]
    messages.append({"role": "user", "content": user_msg})

    tools_used_this_turn = []

    try:
        # 1. Ask OpenAI for the next step
        response = await openai_client.chat.completions.create(
            model="gpt-5.2",
            messages=messages,
            tools=openai_tools
        )

        response_msg = response.choices[0].message
        messages.append(response_msg)

        # 2. Check if a tool was called
        if response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"Executing tool: {name} with args {args}")
                tools_used_this_turn.append(name)

                # Execute tool via the appropriate mode
                if IS_REMOTE:
                    tool_result_text = await call_tool_remote(name, args)
                else:
                    tool_result_text = await call_tool_local(name, args)

                # Report result back to history
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": tool_result_text
                })

            # 3. Get the final response from OpenAI
            final_response = await openai_client.chat.completions.create(
                model="gpt-5.2",
                messages=messages,
                tools=openai_tools
            )
            final_msg = final_response.choices[0].message.content
            messages.append({"role": "assistant", "content": final_msg})

            return ChatResponse(response=final_msg, tools_used=tools_used_this_turn)

        else:
            # No tool was needed
            return ChatResponse(response=response_msg.content, tools_used=[])

    except Exception as e:
        traceback.print_exc()
        return ChatResponse(response=f"An error occurred: {str(e)}", tools_used=[])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_client:app", host="127.0.0.1", port=8000)
