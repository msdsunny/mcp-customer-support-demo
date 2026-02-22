import asyncio
import sys
import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AsyncOpenAI
import traceback

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# -- Globals --
mcp_session = None
mcp_tools = []
openai_tools = []

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Initialize OpenAI Client using Environment Variables
openai_client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL")
)

# Manage state for different sessions/tabs
chat_history = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to the MCP Server
    global mcp_session, mcp_tools, openai_tools
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"], # This is our support_server.py
        env=None
    )
    
    print("Starting MCP connection...")
    
    # We need to keep the context managers alive for the lifespan of the FastAPI app
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            mcp_session = session
            await session.initialize()
            print("Successfully connected to MCP Server!")
            
            # Fetch tools
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
            
            # Yield control back to FastAPI to handle requests
            yield
            
    print("Shutting down MCP connection...")

# Setup FastAPI
app = FastAPI(lifespan=lifespan)

# Setup schemas
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    tools_used: list[str]

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as file:
        return file.read()

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_msg = request.message
    
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
            model="gpt-4.1",
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
                
                # Execute against the MCP server
                result = await mcp_session.call_tool(name, arguments=args)
                tool_result_text = "\n".join(content.text for content in result.content)
                
                # Report result back to history
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": tool_result_text
                })
                
            # 3. Get the final response from OpenAI
            final_response = await openai_client.chat.completions.create(
                model="gpt-4.1",
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
    # Run the uvicorn server directly if script is executed
    uvicorn.run("web_client:app", host="127.0.0.1", port=8000, reload=True)
