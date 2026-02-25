# MCP Client — Vercel Deployment

This is the **MCP Client** component — a FastAPI web app with a chat UI that connects to a remote MCP Server over SSE.

It uses OpenAI's API as the "brain" and the MCP Server's tools as the "hands" to answer customer support questions.

## Setup

### 1. Configure Environment Variables
Copy the example file and fill in your values:
```bash
cp .env.example .env
```

Edit `.env`:
```env
MCP_SERVER_URL=https://your-mcp-server.vercel.app/sse
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 2. Run Locally (Optional)
```bash
pip install -r requirements.txt
python web_client.py
```
Open http://127.0.0.1:8001 in your browser.

### 3. Deploy to Vercel
```bash
npm i -g vercel     # Install Vercel CLI (if not already)
vercel              # Link the project
```

**Set environment variables in Vercel Dashboard:**
| Variable | Description | Required |
|----------|-------------|----------|
| `MCP_SERVER_URL` | Your deployed MCP Server SSE URL | ✅ |
| `OPENAI_API_KEY` | OpenAI API Key | ✅ |
| `OPENAI_BASE_URL` | OpenAI API Base URL | ✅ |

Then deploy:
```bash
vercel --prod
```

### 4. Test
Open `https://<your-client-domain>` and try:
- *"Can you look up recent orders for alice@example.com?"*
- *"Is diana@example.com a VIP customer?"*
- *"Show me all customers"*
