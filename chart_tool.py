"""
chart_tool.py
Makes a bar or line chart from a safe SQL query and saves it as a PNG file.
"""

import uuid
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files, no window (needed on servers)
import matplotlib.pyplot as plt
import pandas as pd
from agents import function_tool

from tools import get_connection, is_safe_sql

CHART_DIR = Path("charts")
BAR_COLOR = "#2a78d6"
TEXT_COLOR = "#52514e"
GRID_COLOR = "#e6e5e1"
MAX_BARS = 15


def make_chart(query: str, chart_type: str, title: str) -> str:
    """Create a chart from a SQL query and save it as an image.

    Args:
        query: A SQLite SELECT query that returns exactly 2 columns:
            first column = labels (city, product, month), second column = numbers.
        chart_type: "bar" to compare items, or "line" for a trend over months.
        title: Short chart title, for example "Sales by city (Rs)".
    """
    safe, reason = is_safe_sql(query)
    if not safe:
        return f"Chart not created: {reason}"

    if chart_type not in ("bar", "line"):
        return "Chart not created: chart_type must be 'bar' or 'line'."

    try:
        conn = get_connection()
        df = pd.read_sql_query(query.strip().rstrip(";"), conn)
        conn.close()
    except Exception as error:
        return f"Chart not created. SQL error: {error}"

    if df.empty:
        return "Chart not created: the query returned no rows."
    if len(df.columns) != 2:
        return "Chart not created: the query must return exactly 2 columns (label, number)."

    df = df.head(MAX_BARS)
    labels = df.iloc[:, 0].astype(str)
    values = pd.to_numeric(df.iloc[:, 1], errors="coerce").fillna(0)

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
    if chart_type == "bar":
        ax.bar(labels, values, color=BAR_COLOR, width=0.6)
    else:
        ax.plot(labels, values, color=BAR_COLOR, linewidth=2, marker="o", markersize=5)

    # Quiet, clean styling: light grid, no box, readable labels
    ax.set_title(title, loc="left", fontsize=13, color="#0b0b0b", pad=12)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_COLOR, length=0)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    if len(labels) > 5:
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    fig.tight_layout()
    CHART_DIR.mkdir(exist_ok=True)
    file_path = CHART_DIR / f"{uuid.uuid4().hex[:10]}.png"
    fig.savefig(file_path)
    plt.close(fig)  # free memory

    return f"CHART_FILE: {file_path.as_posix()}"


make_chart_tool = function_tool(make_chart)