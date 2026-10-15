"""
list_models.py
Shows all Gemini models your API key can use.
Run: uv run list_models.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

for m in client.models.list():
    if "flash" in m.id or "lite" in m.id:
        print(m.id)