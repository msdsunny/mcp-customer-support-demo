# Database Schema and Data

## Database Schema Diagram

```mermaid
erDiagram
    customers ||--o{ orders : has
    
    customers {
        INTEGER id PK
        TEXT name
        TEXT email
        TEXT phone
        BOOLEAN vip_status
    }
    
    orders {
        INTEGER order_id PK
        INTEGER customer_id FK
        TEXT product
        TEXT order_date
        TEXT status
        TEXT tracking_number
    }
```

## Data Values 

### `customers` Table

| id | name | email | phone | vip_status |
|---|---|---|---|---|
| 1 | Alice Smith | alice@example.com | 555-0101 | 1 |
| 2 | Bob Jones | bob@example.com | 555-0102 | 0 |
| 3 | Sunny Maurya | maurya@example.com | 555-0103 | 1 |
| 4 | Diana Prince | diana@example.com | 555-0104 | 1 |
| 5 | Ethan Hunt | ethan@example.com | 555-0105 | 0 |
| 6 | Fiona Green | fiona@example.com | 555-0106 | 0 |
| 7 | George Kumar | george@example.com | 555-0107 | 1 |
| 8 | Hannah Lee | hannah@example.com | 555-0108 | 0 |

### `orders` Table

| order_id | customer_id | product | order_date | status | tracking_number |
|---|---|---|---|---|---|
| 101 | 1 | Premium Laptop | 2023-10-25 | Delivered | TRK-99887766 |
| 102 | 1 | Wireless Mouse | 2023-10-26 | Delivered | TRK-99887767 |
| 103 | 2 | Mechanical Keyboard | 2023-11-01 | Processing | None |
| 104 | 3 | Curved Monitor | 2023-11-05 | Shipped | TRK-11223344 |
| 105 | 3 | Ergonomic Chair | 2023-11-06 | Out for Delivery | TRK-55667788 |
| 106 | 4 | Noise-Cancelling Headphones | 2023-11-10 | Delivered | TRK-22334455 |
| 107 | 4 | USB-C Hub | 2023-11-12 | Delivered | TRK-22334456 |
| 108 | 4 | Webcam 4K | 2023-11-15 | Shipped | TRK-22334457 |
| 109 | 5 | Gaming Mouse | 2023-11-18 | Processing | None |
| 110 | 5 | Mouse Pad XL | 2023-11-18 | Processing | None |
| 111 | 6 | Standing Desk | 2023-11-20 | Shipped | TRK-33445566 |
| 112 | 6 | Desk Lamp LED | 2023-11-21 | Cancelled | None |
| 113 | 7 | MacBook Pro 16" | 2023-11-22 | Out for Delivery | TRK-44556677 |
| 114 | 7 | Apple Magic Keyboard | 2023-11-22 | Delivered | TRK-44556678 |
| 115 | 8 | Portable SSD 2TB | 2023-11-25 | Returned | TRK-55667799 |
