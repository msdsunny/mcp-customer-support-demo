# Model Context Protocol (MCP) Customer Support Demo

This project demonstrates how the **Model Context Protocol (MCP)** enables Large Language Models (LLMs) to securely interact with local, private databases.

An OpenAI-powered web chat interface acts as an AI support agent that can dynamically query a local SQLite database of customer records and orders using an MCP Server.

## Prerequisites
- Python 3.8+
- An OpenAI API Key (or a compatible endpoint, e.g. KodeKloud)

## Project Structure

```
mcp_example/
├── README.md
├── high-level-diagram.md
│
├── mcp-server/              # MCP Server — exposes DB tools
│   ├── server.py            # MCP tools (get_customer_details, get_recent_orders, etc.)
│   ├── create_db.py         # Generates the dummy SQLite database
│   ├── customers.db         # Pre-generated database
│   ├── .env.example         # Server env var template
│   ├── requirements.txt
│   ├── api/index.py         # Vercel entrypoint (for deployment)
│   └── vercel.json          # Vercel routing config
│
└── mcp-client/              # MCP Client — FastAPI chat backend + UI
    ├── web_client.py         # Chat backend (connects to MCP Server)
    ├── static/index.html     # Web-based chat UI
    ├── .env.example          # Client env var template
    ├── requirements.txt
    ├── api/index.py          # Vercel entrypoint (for deployment)
    └── vercel.json           # Vercel routing config
```

**How it works:**
1. **MCP Server** (`mcp-server/server.py`) — the "Hands". Connects to SQLite and exposes tools like `get_customer_details`, `get_recent_orders`, and `get_all_customers` via stdio.
2. **MCP Client** (`mcp-client/web_client.py`) — the "Brain". Runs a FastAPI backend that hosts the chat UI, holds the AI's API key, and decides when to use MCP tools.
3. **Database Generator** (`mcp-server/create_db.py`) — initializes the dummy database (8 customers, 15 orders).

---

## Running Locally

### Step 1: Create & Activate a Virtual Environment

```bash
python -m venv venv
```

Activate it:
- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `.\venv\Scripts\activate.bat`
- **macOS / Linux:** `source venv/bin/activate`

### Step 2: Install Dependencies

Install the dependencies for **both** the server and client:

```bash
pip install -r mcp-server/requirements.txt
pip install -r mcp-client/requirements.txt
```

> [!TIP]
> You also need the `mcp` SDK for local stdio transport. It's included in the server requirements (`mcp[cli]`).

### Step 3: Initialize the Database

```bash
cd mcp-server
python create_db.py
cd ..
```

This creates `mcp-server/customers.db` with 8 sample customers and 15 orders.

### Step 4: Configure Environment Variables

Create a `.env` file inside the `mcp-client/` folder:

```bash
cp mcp-client/.env.example mcp-client/.env
```

Edit `mcp-client/.env` with your values:

```env
# Leave MCP_SERVER_URL empty (or remove it) for local stdio mode
MCP_SERVER_URL=

# Your OpenAI-compatible API credentials
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

> [!IMPORTANT]
> When `MCP_SERVER_URL` is **empty or unset**, the client automatically runs in **local mode** — it spawns `server.py` as a subprocess via stdio. No separate server process is needed!

### Step 5: Start the Application

From the `mcp-client/` directory:

```bash
cd mcp-client
python web_client.py
```

You should see output like:
```
🏠 Running in LOCAL mode → MCP Server via stdio subprocess
[Local] Starting MCP connection via stdio...
[Local] Successfully connected to MCP Server!
[Local] Discovered 3 tools: ['get_customer_details', 'get_recent_orders', 'get_all_customers']
```

### Step 6: Open the Chat UI

Open your browser at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

Try asking questions like:
- *"Can you look up recent orders for alice@example.com?"*
- *"Is diana@example.com a VIP customer?"*
- *"Show me all customers"*

---

## Deploying to Vercel

The MCP Server and MCP Client are deployed as **two separate Vercel projects**.

### 1. Deploy the MCP Server

```bash
cd mcp-server
python create_db.py         # Generate the database (if not already done)
vercel                       # Link project to Vercel
vercel --prod                # Deploy to production
```

Note the deployed URL (e.g., `https://mcp-server-xxx.vercel.app`).

> Set `DISABLE_CUSTOMER_LOOKUP=true` in the Vercel Dashboard env vars to disable the "list all customers" tool.

### 2. Deploy the MCP Client

```bash
cd mcp-client
vercel                       # Link project to Vercel
```

**Set these environment variables in the Vercel Dashboard:**

| Variable | Value |
|----------|-------|
| `MCP_SERVER_URL` | `https://your-mcp-server.vercel.app` |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` |

Then deploy:

```bash
vercel --prod
```

### 3. Test

Open your client URL and chat with the AI — it will call the remote MCP Server to query the database!
