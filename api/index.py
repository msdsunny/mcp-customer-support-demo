import os
import sys

# Add the root directory to the python path so Vercel can find `server.py` and `web_client.py`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import mcp

# Vercel needs an ASGI app object called `app` to execute.
# We expose the MCP SSE Server directly to the web!
app = mcp.sse_app()
