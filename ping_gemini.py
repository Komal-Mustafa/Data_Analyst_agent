"""
ping_gemini.py
Sends ONE tiny message to Gemini to check the connection and model.
Run: uv run ping_gemini.py
"""

import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=30,
)

print("Testing model:", model_name)
start = time.time()
try:
    reply = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "Say OK"}],
    )
    print("Works! Reply:", reply.choices[0].message.content)
except Exception as error:
    print("Failed:", error)
print(f"Time: {time.time() - start:.1f} seconds")