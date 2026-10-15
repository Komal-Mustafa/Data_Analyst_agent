"""
main.py
Chat with the Data Analyst Agent in the terminal. It remembers the conversation.
Run: uv run main.py
"""

import asyncio

from agents import InputGuardrailTripwireTriggered, Runner, SQLiteSession

from analyst_agent import analyst_agent

MAX_TURNS = 10


def find_chart(result) -> str | None:
    """Look through the agent's steps and return the chart file path, if one was made."""
    for item in result.new_items:
        if item.type == "tool_call_output_item":
            output = str(item.output)
            if output.startswith("CHART_FILE:"):
                return output.replace("CHART_FILE:", "").strip()
    return None


async def main():
    session = SQLiteSession("manager_1", "memory.db")
    print("Data Analyst Agent. Ask about sales, products, cities or trends.")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue

        try:
            result = await Runner.run(analyst_agent, question, session=session, max_turns=MAX_TURNS)
        except InputGuardrailTripwireTriggered:
            print("Analyst: I can only answer questions about the shop's sales data.\n")
            continue
        except Exception as error:
            if "429" in str(error):
                print("Analyst: Daily AI limit reached. Please try again later.\n")
            elif "503" in str(error):
                print("Analyst: The AI service is busy right now. Please try again in a few minutes.\n")
            else:
                print(f"Analyst: Something went wrong: {error}\n")
            continue

        print(f"\nAnalyst: {result.final_output}")
        chart = find_chart(result)
        if chart:
            print(f"(Chart saved: {chart})")
        print()


if __name__ == "__main__":
    asyncio.run(main())
