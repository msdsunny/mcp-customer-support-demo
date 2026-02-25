import sqlite3
import os

def create_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customers.db")
    
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
        (3, "Sunny Maurya", "maurya@example.com", "555-0103", True),
        (4, "Diana Prince", "diana@example.com", "555-0104", True),
        (5, "Ethan Hunt", "ethan@example.com", "555-0105", False),
        (6, "Fiona Green", "fiona@example.com", "555-0106", False),
        (7, "George Kumar", "george@example.com", "555-0107", True),
        (8, "Hannah Lee", "hannah@example.com", "555-0108", False),
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers_data)

    orders_data = [
        (101, 1, "Premium Laptop", "2023-10-25", "Delivered", "TRK-99887766"),
        (102, 1, "Wireless Mouse", "2023-10-26", "Delivered", "TRK-99887767"),
        (103, 2, "Mechanical Keyboard", "2023-11-01", "Processing", None),
        (104, 3, "Curved Monitor", "2023-11-05", "Shipped", "TRK-11223344"),
        (105, 3, "Ergonomic Chair", "2023-11-06", "Out for Delivery", "TRK-55667788"),
        (106, 4, "Noise-Cancelling Headphones", "2023-11-10", "Delivered", "TRK-22334455"),
        (107, 4, "USB-C Hub", "2023-11-12", "Delivered", "TRK-22334456"),
        (108, 4, "Webcam 4K", "2023-11-15", "Shipped", "TRK-22334457"),
        (109, 5, "Gaming Mouse", "2023-11-18", "Processing", None),
        (110, 5, "Mouse Pad XL", "2023-11-18", "Processing", None),
        (111, 6, "Standing Desk", "2023-11-20", "Shipped", "TRK-33445566"),
        (112, 6, "Desk Lamp LED", "2023-11-21", "Cancelled", None),
        (113, 7, 'MacBook Pro 16"', "2023-11-22", "Out for Delivery", "TRK-44556677"),
        (114, 7, "Apple Magic Keyboard", "2023-11-22", "Delivered", "TRK-44556678"),
        (115, 8, "Portable SSD 2TB", "2023-11-25", "Returned", "TRK-55667799"),
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders_data)

    conn.commit()
    conn.close()
    print("Database 'customers.db' created successfully with dummy data.")

if __name__ == "__main__":
    create_database()
