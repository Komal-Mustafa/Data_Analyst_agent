"""
test_sql_agent.py
Asks the SQL Agent 2 questions and shows which tools it called.
Uses about 6-8 Gemini requests. Run: uv run test_sql_agent.py
"""

import asyncio

from agents import Runner

from sql_agent import sql_agent

QUESTIONS = [
    "Which city had the highest sales?",
    "Which product was returned the most times?",
]


async def ask(question: str):
    print("=" * 60)
    print("QUESTION:", question)
    try:
        result = await Runner.run(sql_agent, question, max_turns=6)
    except Exception as error:
        if "429" in str(error):
            print("Daily Gemini limit reached. Try again later.")
        else:
            print("Error:", error)
        return

    print("\nTools the agent used:")
    for item in result.new_items:
        if item.type == "tool_call_item":
            print(f"  - {item.raw_item.name}({item.raw_item.arguments})")

    print("\nANSWER:\n", result.final_output)


async def main():
    for question in QUESTIONS:
        await ask(question)


if __name__ == "__main__":
    asyncio.run(main())