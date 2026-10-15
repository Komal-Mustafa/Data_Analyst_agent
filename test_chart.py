"""
test_chart.py
Tests the chart tool without the AI (no API calls).
Run: uv run test_chart.py  -> then open the PNG files in the charts folder.
"""

from chart_tool import make_chart

print(make_chart(
    """SELECT city, SUM(total_amount) AS sales
       FROM orders WHERE status = 'delivered'
       GROUP BY city ORDER BY sales DESC""",
    "bar",
    "Delivered sales by city (Rs)",
))

print(make_chart(
    """SELECT strftime('%Y-%m', order_date) AS month, SUM(total_amount) AS sales
       FROM orders WHERE status = 'delivered'
       GROUP BY month ORDER BY month""",
    "line",
    "Monthly delivered sales (Rs)",
))

print(make_chart("DROP TABLE orders", "bar", "Should be blocked"))
print(make_chart("SELECT city FROM orders", "bar", "Wrong column count"))