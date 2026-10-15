"""
test_tools.py
Tests the database tools without using the AI (no API calls).
Run: uv run test_tools.py
"""

from tools import get_schema, is_safe_sql, run_sql

print("=== 1. Schema ===")
print(get_schema())

print("\n=== 2. Sales by city ===")
print(run_sql("""
    SELECT city, SUM(total_amount) AS sales
    FROM orders
    WHERE status = 'delivered'
    GROUP BY city
    ORDER BY sales DESC
"""))

print("\n=== 3. Top 3 products ===")
print(run_sql("""
    SELECT p.name, SUM(o.quantity) AS units_sold
    FROM orders o JOIN products p ON o.product_id = p.product_id
    GROUP BY p.name
    ORDER BY units_sold DESC
    LIMIT 3
"""))

print("\n=== 4. Safety checks (all should be blocked) ===")
dangerous = [
    "DELETE FROM orders",
    "DROP TABLE orders",
    "SELECT * FROM orders; DROP TABLE orders",
    "UPDATE orders SET total_amount = 0",
]
for query in dangerous:
    print(f"{query!r:50} -> {run_sql(query)}")

print("\n=== 5. Wrong column name (friendly error) ===")
print(run_sql("SELECT revenue FROM orders"))

print("\n=== 6. Safe query passes check ===")
print(is_safe_sql("SELECT COUNT(*) FROM orders"))