from pathlib import Path

import groq
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.agent import run_agent
from app.config import settings
from app.limits import rate_limit

router = APIRouter()


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    file_name: str
    history: list[dict] = []


def clean_history(history: list[dict]) -> list[dict]:
    """Keep only plain user/assistant text, so a client cannot inject system or tool messages."""
    cleaned = [
        {"role": m["role"], "content": m["content"][:2000]}
        for m in history
        if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str)
    ]
    return cleaned[-6:]


@router.post("/ask", dependencies=[Depends(rate_limit)])
def ask(req: AskRequest):
    file_name = Path(req.file_name).name
    if not (settings.upload_dir / file_name).exists():
        raise HTTPException(status_code=404, detail="Upload a CSV file first.")

    try:
        return run_agent(req.question, file_name, clean_history(req.history))
    except groq.RateLimitError:
        raise HTTPException(status_code=429, detail="The AI model is rate limited. Wait a minute and try again.")
    except groq.APIError:
        raise HTTPException(status_code=502, detail="The AI model returned an error. Please try again.")