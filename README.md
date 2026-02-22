# Model Context Protocol (MCP) Customer Support Demo

This project demonstrates how the **Model Context Protocol (MCP)** enables Large Language Models (LLMs) to securely interact with local, private databases. 

In this demo, an OpenAI-powered web chat interface acts as an AI support agent that can dynamically query a local SQLite database of customer records and orders using an MCP Server!

## Prerequisites
- Python 3.8+
- An OpenAI API Key (or a compatible endpoint)

## Project Architecture
1. `server.py`: The **MCP Server**. This acts as the "Hands". It connects to the SQLite database and exposes tools (`get_customer_details`, `get_recent_orders`) via stdio.
2. `web_client.py`: The **MCP Client**. This acts as the "Brain". It runs a FastAPI backend that hosts the chat UI, securely holds the AI's API key, and decides when to use the MCP tools to answer user questions.
3. `create_db.py`: A helper script to initialize the dummy local database.
4. `static/index.html`: The web-based frontend chat interface.

---

## Setup Instructions

### 1. Create a Virtual Environment
It is highly recommended to run this in a Python virtual environment to keep dependencies clean.
```bash
python -m venv venv
```

**Activate the environment:**
- On Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
- On Windows (CMD): `.\venv\Scripts\activate.bat`
- On macOS/Linux: `source venv/bin/activate`

### 2. Install Dependencies
Install all required libraries, including `mcp`, `openai`, and `fastapi`:
```bash
pip install -r requirements.txt
```

### 3. Initialize the Database
Before running the application, you need to generate the dummy `customers.db` file.
```bash
python create_db.py
```
You should see a message confirming the database was created.

### 4. Provide your LLM Credentials
Open `web_client.py` in your code editor. Locate the `AsyncOpenAI` client initialization near the top of the file and ensure your `api_key` and `base_url` are configured properly for your provider.

---

## Running the Demo

1. Start the FastAPI web application:
```bash
python web_client.py
```

2. Open your web browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

3. You can now chat with the AI! Try asking it questions like:
   - *"Can you look up recent orders for alice@example.com?"*
   - *"Is maurya@example.com a VIP customer?"*

Watch as the AI realizes it doesn't know the answer, uses the MCP Protocol to call the local database tools, reads the response, and formats a perfect answer for you!

## Deploying to Vercel

The MCP Server is configured to deploy directly to Vercel as an SSE Serverless API.

1. Install the Vercel CLI: 
pm i -g vercel`n2. Run ercel in your terminal to log in and link the project.
3. Run ercel --prod to deploy it.

Once deployed, your MCP Server will be available over the internet via SSE at https://<your-vercel-domain>/api/mcp.
