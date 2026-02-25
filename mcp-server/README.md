# MCP Server — Vercel Deployment

This is the **MCP Server** component, deployed as a standalone SSE endpoint on Vercel.

It exposes customer support tools (`get_customer_details`, `get_recent_orders`, `get_all_customers`) that any MCP client can call over SSE.

## Setup

### 1. Generate the Database
```bash
python create_db.py
```

### 2. Deploy to Vercel
```bash
npm i -g vercel     # Install Vercel CLI (if not already)
vercel              # Link the project
vercel --prod       # Deploy to production
```

### 3. Note Your URL
After deployment, your MCP Server will be available at:
```
https://<your-vercel-domain>/sse
```

You'll need this URL to configure the MCP Client.

## Environment Variables (Vercel Dashboard)
| Variable | Description | Default |
|----------|-------------|---------|
| `DISABLE_CUSTOMER_LOOKUP` | Disable the "list all customers" tool | `false` |

## Testing the SSE Endpoint
Once deployed, you can verify it works by visiting `https://<your-domain>/sse` — you should see an SSE connection start.
