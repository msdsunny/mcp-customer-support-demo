import sqlite3
import os

def create_database():
    db_path = "customers.db"
    
    # Remove if it already exists for a clean slate
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Customers Table
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        vip_status BOOLEAN
    )
    """)

    # Create Orders Table
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product TEXT,
        order_date TEXT,
        status TEXT,
        tracking_number TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    """)

    # Insert Dummy Data
    customers_data = [
        (1, "Alice Smith", "alice@example.com", "555-0101", True),
        (2, "Bob Jones", "bob@example.com", "555-0102", False),
        (3, "Sunny Maurya", "maury@example.com", "555-0103", True)
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers_data)

    orders_data = [
        (101, 1, "Premium Laptop", "2023-10-25", "Delivered", "TRK-99887766"),
        (102, 1, "Wireless Mouse", "2023-10-26", "Delivered", "TRK-99887767"),
        (103, 2, "Mechanical Keyboard", "2023-11-01", "Processing", None),
        (104, 3, "Curved Monitor", "2023-11-05", "Shipped", "TRK-11223344"),
        (105, 3, "Ergonomic Chair", "2023-11-06", "Out for Delivery", "TRK-55667788")
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders_data)

    conn.commit()
    conn.close()
    print("Database 'customers.db' created successfully with dummy data.")

if __name__ == "__main__":
    create_database()
