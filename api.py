"""
api.py
FastAPI server for the Data Analyst Agent.
Run locally: uv run uvicorn api:app --reload
Then open http://127.0.0.1:8000
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from agents import InputGuardrailTripwireTriggered, Runner, SQLiteSession

import create_data
from analyst_agent import analyst_agent
from main import MAX_TURNS, find_chart

# On a fresh server (like Render) the database does not exist yet, so create it.
if not Path(create_data.DB_FILE).exists():
    create_data.main()

Path("charts").mkdir(exist_ok=True)

app = FastAPI(title="Data Analyst Agent")
app.mount("/charts", StaticFiles(directory="charts"), name="charts")


class AskRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    question: str = Field(min_length=1, max_length=500)


class AskResponse(BaseModel):
    answer: str
    chart_url: str | None = None


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    session = SQLiteSession(request.session_id, "memory.db")
    try:
        result = await Runner.run(
            analyst_agent, request.question, session=session, max_turns=MAX_TURNS
        )
    except InputGuardrailTripwireTriggered:
        return AskResponse(answer="I can only answer questions about the shop's sales data.")
    except Exception as error:
        if "429" in str(error):
            raise HTTPException(status_code=429, detail="Daily AI limit reached. Please try again later.")
        if "503" in str(error) or "timed out" in str(error).lower():
            raise HTTPException(status_code=503, detail="The AI service is busy right now. Please try again in a few minutes.")
        print("Error:", error)
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")

    chart = find_chart(result)
    return AskResponse(
        answer=str(result.final_output),
        chart_url=f"/{chart}" if chart else None,
    )