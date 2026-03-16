# Technologies Used

This document outlines the core technologies, frameworks, libraries, and platforms used to build the MCP Customer Support Demo project.

## 1. Programming Languages & Core
- **Python (3.x)**: The primary programming language used for both the `mcp-client` and `mcp-server` backend environments.
- **SQL / SQLite**: Used natively for persistent data storage (`customers.db`), enabling lightweight local querying without the need for a separate database server.
- **HTML/CSS/JavaScript**: Used for the frontend Chat UI implementation, served as static assets by the client.

## 2. Frameworks & Servers
- **FastAPI**: Used extensively in both the client and the server. It powers the REST API endpoints (`/api/chat`, `/tools`, `/call_tool`), the static file hosting, and interfaces closely with the MCP endpoints.
- **Uvicorn**: The ASGI web server implementation used to run the FastAPI applications locally during development.

## 3. APIs & Protocols
- **Model Context Protocol (MCP)**: The standard protocol used to integrate the LLM with the defined business tools. This project utilizes the official `mcp` Python SDK (including `stdio` transports for local sessions and `sse` logic for remote sessions).
- **OpenAI API**: The project uses the official `openai` Python library to communicate asynchronously with OpenAI's `gpt-5.2` model for chat completions and tool-call planning.

## 4. Key Python Libraries
- **Pydantic**: Used for robust data validation and serialization (e.g., standardizing Chat Requests/Responses).
- **HTTPX**: A fully featured HTTP client, used asynchronously in the `mcp-client` to make remote REST calls to the Vercel-hosted MCP endpoint.
- **Python-dotenv**: Used to reliably load environment variables (like API keys and server URLs) from `.env` files during local development.

## 5. Deployment & Platform
- **Vercel**: The target deployment platform. The project is split into two independent serverless configurations leveraging Vercel's `api/index.py` serverless function conventions.
- **Git**: Used for version control across the project.
