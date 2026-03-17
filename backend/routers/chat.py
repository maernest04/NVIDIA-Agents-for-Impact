from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.agent import build_agent, run_agent

router = APIRouter(prefix="/chat", tags=["chat"])

# Lazily initialised on first request so the app starts without a valid API key.
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


class HistoryMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[HistoryMessage]] = None


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
    
    # Convert history to the format the agent expects
    history = []
    if request.history:
        history = [{"role": h.role, "content": h.content} for h in request.history]
    
    response = run_agent(_get_agent(), request.message, history=history)
    return ChatResponse(response=response)
