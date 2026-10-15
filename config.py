"""
config.py
Connects the OpenAI Agents SDK to Google Gemini.
"""

import os

from dotenv import load_dotenv
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")

# No OpenAI key, so turn off tracing (otherwise you get a 401 tracing error)
set_tracing_disabled(True)

# Model name comes from .env if you set it there, otherwise this default is used.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=60,
    max_retries=3,  # retry automatically when Gemini is busy (503)
)

model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)