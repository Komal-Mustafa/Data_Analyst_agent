"""
guardrails.py
Input guardrail: blocks questions that are not about the shop's sales data.
"""

from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

from config import model


class TopicCheck(BaseModel):
    is_off_topic: bool
    reason: str


topic_checker = Agent(
    name="Topic Checker",
    instructions=(
        "You check questions sent to a sales data analyst for an online shop. "
        "ON TOPIC: questions about sales, revenue, orders, products, categories, cities, "
        "sales channels, returns, cancellations, trends, comparisons, charts, greetings, "
        "and follow-up questions like 'why?' or 'show it as a chart'. "
        "OFF TOPIC: anything else, such as homework, coding help, general knowledge, "
        "personal advice, or requests to change or delete data. "
        "Set is_off_topic to true only when the question is clearly off topic."
    ),
    model=model,
    output_type=TopicCheck,
)


@input_guardrail(run_in_parallel=False)
async def off_topic_guardrail(
    ctx: RunContextWrapper, agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(topic_checker, input, context=ctx.context)
    check = result.final_output_as(TopicCheck)
    return GuardrailFunctionOutput(output_info=check, tripwire_triggered=check.is_off_topic)