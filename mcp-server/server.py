import sqlite3
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Create the MCP Server
mcp = FastMCP("Support Database Server")

# Use absolute path relative to this file so it works in serverless environments
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customers.db")

def query_db(query: str, args: tuple = ()) -> list[dict]:
    """Helper function to execute a database query and return rows as dictionaries."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # Configure connection to return dictionary-like rows
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        if 'conn' in locals():
            conn.close()

@mcp.tool()
def get_customer_details(email: str) -> str:
    """Find a customer's basic details and VIP status by their email address."""
    query = "SELECT id, name, phone, vip_status FROM customers WHERE email = ?"
    results = query_db(query, (email,))
    
    if not results:
        return f"No customer found with email: {email}"
    
    # Format the dictionary row into a clean string for the LLM
    customer = results[0]
    vip_str = "Yes" if customer["vip_status"] else "No"
    
    return (
        f"Customer Details:\n"
        f"- ID: {customer['id']}\n"
        f"- Name: {customer['name']}\n"
        f"- Phone: {customer['phone']}\n"
        f"- VIP Customer: {vip_str}"
    )

@mcp.tool()
def get_recent_orders(email: str) -> str:
    """Get the recent orders and shipping status for a customer by their email address."""
    # This query joins the customers table and orders table
    query = """
        SELECT o.order_id, o.product, o.order_date, o.status, o.tracking_number 
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE c.email = ?
        ORDER BY o.order_date DESC
    """
    results = query_db(query, (email,))
    
    if not results:
        return f"No orders found for customer: {email}"
    
    if "error" in results[0]:
         return f"Database error: {results[0]['error']}"
         
    # Format the orders into a readable list
    output = f"Recent Orders for {email}:\n\n"
    for order in results:
        tracking = order["tracking_number"] if order["tracking_number"] else "Not yet assigned"
        output += (
            f"Order #{order['order_id']} - {order['product']}\n"
            f"  Date: {order['order_date']}\n"
            f"  Status: {order['status']}\n"
            f"  Tracking: {tracking}\n"
            f"  ---\n"
        )
        
    return output

@mcp.tool()
def get_all_customers() -> str:
    """Retrieve a list of all registered customers with their names and emails."""
    
    # 1. Check the Environment Variable Feature Flag
    if os.environ.get("DISABLE_CUSTOMER_LOOKUP", "false").lower() == "true":
        return "ERROR: The Administrator has temporarily disabled the ability to list all customers."
        
    query = "SELECT id, name, email, vip_status FROM customers ORDER BY name ASC"
    results = query_db(query)
    
    if not results:
        return "No customers found in the database."
        
    if "error" in results[0]:
         return f"Database error: {results[0]['error']}"
         
    output = "All Registered Customers:\n\n"
    for user in results:
        vip_star = "⭐ VIP " if user["vip_status"] else ""
        output += f"{user['id']}. {vip_star}{user['name']} ({user['email']})\n"
        
    return output

if __name__ == "__main__":
    # Run over stdio for local development
    mcp.run(transport='stdio')
