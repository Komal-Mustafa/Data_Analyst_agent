"""
test_guardrail.py
Sends ONE off-topic question. The guard should block it.
Uses only 1 Gemini request. Run: uv run test_guardrail.py
"""

import asyncio

from agents import InputGuardrailTripwireTriggered, Runner

from analyst_agent import analyst_agent

QUESTION = "Can you solve my physics homework?"


async def main():
    print("QUESTION:", QUESTION)
    try:
        result = await Runner.run(analyst_agent, QUESTION, max_turns=10)
        print("NOT blocked. Answer:", result.final_output)
    except InputGuardrailTripwireTriggered as blocked:
        reason = blocked.guardrail_result.output.output_info.reason
        print("BLOCKED by guardrail ")
        print("Reason:", reason)
    except Exception as error:
        if "429" in str(error):
            print("Daily Gemini limit reached. Try again later.")
        elif "503" in str(error):
            print("Gemini is busy right now. Wait a few minutes and try again.")
        else:
            print("Error:", error)


if __name__ == "__main__":
    asyncio.run(main())