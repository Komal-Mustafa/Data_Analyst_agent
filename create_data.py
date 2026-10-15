"""
create_data.py
Creates a fake sales database (sales.db) for a Pakistani online shop.
Run once: uv run create_data.py
"""

import random
import sqlite3
from datetime import date, timedelta

random.seed(42)  # same data every time you run it
DB_FILE = "sales.db"

PRODUCTS = [
    (1, "Lawn Suit", "Clothing", 4500),
    (2, "Embroidered Kurta", "Clothing", 3200),
    (3, "Running Shoes", "Footwear", 7500),
    (4, "Leather Sandals", "Footwear", 2800),
    (5, "Wireless Headphones", "Electronics", 6800),
    (6, "Smart Watch", "Electronics", 25000),
    (7, "Mobile Cover", "Accessories", 800),
    (8, "Handbag", "Accessories", 3900),
]

CITIES = ["Lahore", "Karachi", "Islamabad", "Faisalabad", "Multan"]
CHANNELS = ["Website", "WhatsApp", "Store"]
STATUSES = ["delivered"] * 8 + ["returned", "cancelled"]  # mostly delivered


def create_tables(cur):
    cur.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name       TEXT,
            category   TEXT,
            price      INTEGER
        );

        CREATE TABLE orders (
            order_id     INTEGER PRIMARY KEY,
            order_date   TEXT,
            product_id   INTEGER,
            quantity     INTEGER,
            city         TEXT,
            channel      TEXT,
            status       TEXT,
            total_amount INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """)


def insert_data(cur):
    cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", PRODUCTS)

    start = date(2026, 1, 1)
    for order_id in range(1, 601):
        product = random.choice(PRODUCTS)
        quantity = random.randint(1, 3)
        order_date = start + timedelta(days=random.randint(0, 272))  # Jan to Sep
        cur.execute(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                order_id,
                order_date.isoformat(),
                product[0],
                quantity,
                random.choice(CITIES),
                random.choice(CHANNELS),
                random.choice(STATUSES),
                product[3] * quantity,
            ),
        )


def main():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    create_tables(cur)
    insert_data(cur)
    conn.commit()

    count = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total = cur.execute("SELECT SUM(total_amount) FROM orders WHERE status='delivered'").fetchone()[0]
    print(f"Database created: {DB_FILE}")
    print(f"Orders: {count}")
    print(f"Delivered sales: Rs {total:,}")
    conn.close()


if __name__ == "__main__":
    main()