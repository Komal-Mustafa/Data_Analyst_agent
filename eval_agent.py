"""
eval_agent.py
Checks if the SQL Agent gives CORRECT answers.

For each test question we already know the right answer (we calculate it
ourselves with plain SQL). Then we ask the agent the same question and
check that its answer contains the right name or number.

Uses about 2-3 Gemini requests per question (6 questions = ~15 requests).
Run: uv run eval_agent.py
"""

import asyncio
import json
import re
import sqlite3
from datetime import datetime

from agents import Runner

from sql_agent import sql_agent
from tools import DB_FILE

# Each test: a question + the SQL that gives the TRUE answer.
# The true SQL returns one row. "check" says which column(s) must appear in the agent's answer.
TESTS = [
    {
        "question": "Which city had the highest sales?",
        "truth_sql": """SELECT city, SUM(total_amount) FROM orders WHERE status='delivered'
                        GROUP BY city ORDER BY 2 DESC LIMIT 1""",
        "check": [0, 1],  # city name and the amount
    },
    {
        "question": "Which product was returned the most times?",
        "truth_sql": """SELECT p.name, COUNT(*) FROM orders o JOIN products p ON o.product_id = p.product_id
                        WHERE o.status='returned' GROUP BY p.name ORDER BY 2 DESC LIMIT 1""",
        "check": [0],  # product name
    },
    {
        "question": "What were the total delivered sales in March 2026?",
        "truth_sql": """SELECT SUM(total_amount) FROM orders
                        WHERE status='delivered' AND strftime('%Y-%m', order_date)='2026-03'""",
        "check": [0],  # the amount
    },
    {
        "question": "Which sales channel had the most delivered orders?",
        "truth_sql": """SELECT channel, COUNT(*) FROM orders WHERE status='delivered'
                        GROUP BY channel ORDER BY 2 DESC LIMIT 1""",
        "check": [0],  # channel name
    },
    {
        "question": "How many orders were cancelled?",
        "truth_sql": "SELECT COUNT(*) FROM orders WHERE status='cancelled'",
        "check": [0],  # the count
    },
    {
        "question": "Which product category had the highest sales?",
        "truth_sql": """SELECT p.category, SUM(o.total_amount) FROM orders o JOIN products p ON o.product_id = p.product_id
                        WHERE o.status='delivered' GROUP BY p.category ORDER BY 2 DESC LIMIT 1""",
        "check": [0],  # category name
    },
]

PAUSE_SECONDS = 5  # small pause between questions, gentle on the free quota


def true_answer(sql: str) -> tuple:
    """Run our own trusted SQL to get the correct answer."""
    conn = sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)
    row = conn.execute(sql).fetchone()
    conn.close()
    return row


def value_found(value, text: str) -> bool:
    """Is this value in the agent's answer? Numbers can be written with or without commas."""
    if isinstance(value, (int, float)):
        number = int(value)
        # whole numbers only, so 61 does not match inside 1615
        return any(re.search(rf"(?<![\d,]){re.escape(form)}(?![\d,])", text)
                   for form in (str(number), f"{number:,}"))
    return str(value).lower() in text.lower()


async def run_eval():
    results = []
    passed = 0

    for n, test in enumerate(TESTS, start=1):
        truth = true_answer(test["truth_sql"])
        expected = [truth[i] for i in test["check"]]
        print(f"\n[{n}/{len(TESTS)}] {test['question']}")
        print(f"   expected: {expected}")

        try:
            result = await Runner.run(sql_agent, test["question"], max_turns=6)
            answer = str(result.final_output)
        except Exception as error:
            if "429" in str(error):
                print("   Daily Gemini limit reached. Stopping here.")
                break
            answer = f"ERROR: {error}"

        ok = all(value_found(v, answer) for v in expected)
        passed += ok
        print("   PASS" if ok else f"   FAIL\n   agent said: {answer[:300]}")

        results.append({
            "question": test["question"],
            "expected": [str(v) for v in expected],
            "passed": ok,
            "agent_answer": answer,
        })
        await asyncio.sleep(PAUSE_SECONDS)

    total = len(results)
    if total:
        score = round(100 * passed / total)
        print(f"\nScore: {passed}/{total} correct ({score}%)")

        with open("eval_results.json", "w", encoding="utf-8") as f:
            json.dump({"run_at": datetime.now().isoformat(timespec="seconds"),
                       "score": f"{passed}/{total}", "results": results}, f, indent=2)
        print("Details saved to eval_results.json")


if __name__ == "__main__":
    asyncio.run(run_eval())