import os
import sys
import json

# Add the root directory to the python path so Vercel can find `server.py`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from server import mcp, get_customer_details, get_recent_orders, get_all_customers

# Create a simple REST API wrapper around the MCP tools.
# MCP's SSE/Streamable HTTP transports require persistent connections
# which don't work on Vercel serverless. Instead, we expose the tools
# as simple REST endpoints that the client can call directly.

app = FastAPI(title="MCP Support Server")

# Map tool names to functions
TOOLS = {
    "get_customer_details": get_customer_details,
    "get_recent_orders": get_recent_orders,
    "get_all_customers": get_all_customers,
}

@app.get("/")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "tools": list(TOOLS.keys())}

@app.get("/tools")
async def list_tools():
    """List available MCP tools with their schemas (mimics MCP tool listing)."""
    tools_list = []
    for tool in mcp._tool_manager.list_tools():
        tools_list.append({
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.parameters,
        })
    return {"tools": tools_list}

@app.post("/call_tool")
async def call_tool(request: Request):
    """Execute an MCP tool by name with provided arguments."""
    body = await request.json()
    tool_name = body.get("name")
    arguments = body.get("arguments", {})

    if tool_name not in TOOLS:
        return JSONResponse(
            status_code=404,
            content={"error": f"Tool '{tool_name}' not found. Available: {list(TOOLS.keys())}"}
        )

    try:
        result = TOOLS[tool_name](**arguments)
        return {"result": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
