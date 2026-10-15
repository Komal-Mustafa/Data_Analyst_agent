"""
test_analyst.py
Asks the Analyst Agent ONE question. Shows the steps, the answer and the chart.
Uses about 4-6 Gemini requests. Run: uv run test_analyst.py
"""

import asyncio

from agents import Runner

from analyst_agent import analyst_agent

QUESTION = "Which city had the highest sales?"


async def main():
    print("QUESTION:", QUESTION)
    try:
        result = await Runner.run(analyst_agent, QUESTION, max_turns=10)
    except Exception as error:
        if "429" in str(error):
            print("Daily Gemini limit reached. Try again later.")
        elif "503" in str(error):
            print("Gemini is busy right now. Wait a few minutes and try again.")
        else:
            print("Error:", error)
        return

    print("\nSteps the boss agent took:")
    chart = None
    for item in result.new_items:
        if item.type == "tool_call_item":
            print(f"  - called {item.raw_item.name}")
        if item.type == "tool_call_output_item" and str(item.output).startswith("CHART_FILE:"):
            chart = str(item.output).replace("CHART_FILE:", "").strip()

    print("\nANSWER:\n", result.final_output)
    if chart:
        print(f"\nChart saved: {chart}")


if __name__ == "__main__":
    asyncio.run(main())