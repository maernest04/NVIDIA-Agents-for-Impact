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


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
    response = run_agent(_get_agent(), request.message)
    return ChatResponse(response=response)
