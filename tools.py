"""
tools.py
Database tools for the Data Analyst Agent.
The agent can only READ the database. It can never change it.
"""

import re
import sqlite3

import pandas as pd
from agents import function_tool

DB_FILE = "sales.db"
MAX_ROWS = 50  # never send huge results to the AI

# Words that change data. If any appear, we block the query.
FORBIDDEN_WORDS = [
    "insert", "update", "delete", "drop", "alter", "create",
    "replace", "attach", "detach", "pragma", "vacuum", "truncate",
]


def get_connection():
    """Open the database in READ-ONLY mode."""
    return sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)


def get_schema() -> str:
    """Return all tables and their columns in the sales database.

    Always call this first, before writing any SQL query.
    """
    conn = get_connection()
    cur = conn.cursor()
    tables = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    lines = []
    for (table,) in tables:
        columns = cur.execute(f"PRAGMA table_info({table})").fetchall()
        col_text = ", ".join(f"{col[1]} ({col[2]})" for col in columns)
        lines.append(f"Table {table}: {col_text}")
    conn.close()
    return "\n".join(lines)


def is_safe_sql(query: str) -> tuple[bool, str]:
    """Check that a query only reads data. Returns (is_safe, reason)."""
    clean = query.strip().rstrip(";").strip()
    lower = clean.lower()

    if not clean:
        return False, "The query is empty."
    if not (lower.startswith("select") or lower.startswith("with")):
        return False, "Only SELECT queries are allowed."
    if ";" in clean:
        return False, "Only one query at a time is allowed."
    for word in FORBIDDEN_WORDS:
        if re.search(rf"\b{word}\b", lower):
            return False, f"The word '{word.upper()}' is not allowed."
    return True, "ok"


def run_sql(query: str) -> str:
    """Run a read-only SQL SELECT query on the sales database and return the result as a table.

    Args:
        query: One SQLite SELECT query. Use column names exactly as shown by get_schema.
    """
    safe, reason = is_safe_sql(query)
    if not safe:
        return f"Query blocked: {reason}"

    try:
        conn = get_connection()
        df = pd.read_sql_query(query.strip().rstrip(";"), conn)
        conn.close()
    except Exception as error:
        return f"SQL error: {error}. Check the column names with get_schema and try again."

    if df.empty:
        return "The query returned no rows."

    note = ""
    if len(df) > MAX_ROWS:
        note = f"\n(Showing first {MAX_ROWS} of {len(df)} rows.)"
        df = df.head(MAX_ROWS)
    return df.to_string(index=False) + note


# Wrap plain functions as agent tools (plain functions stay testable)
get_schema_tool = function_tool(get_schema)
run_sql_tool = function_tool(run_sql)