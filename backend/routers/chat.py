<<<<<<< HEAD
import sqlite3
from typing import Any
=======
from typing import List, Optional
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.agent import build_agent, run_agent
from database import DB_PATH

router = APIRouter(prefix="/chat", tags=["chat"])

# Lazily initialised on first request so the app starts without a valid API key.
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


<<<<<<< HEAD
def _search_resources(query: str, limit: int = 3) -> list[dict[str, Any]]:
    """Search the DB and map rows to the shape ResourceCard expects."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT id, resource_name, phone_number, email, description
        FROM campus_resources
        WHERE resource_name LIKE ? OR description LIKE ?
        LIMIT ?
        """,
        (f"%{query}%", f"%{query}%", limit),
    ).fetchall()
    con.close()

    results = []
    for r in rows:
        desc = r["description"] or ""
        availability = "24/7" if "24/7" in desc else "Call for current hours"
        results.append({
            "id": str(r["id"]),
            "name": r["resource_name"],
            "phone": r["phone_number"] or "Contact for info",
            "availability": availability,
            "whyItHelps": desc,
            "callScript": (
                f"Hi, I'm reaching out because I need help. "
                f"I was referred to {r['resource_name']} for support."
            ),
        })
    return results
=======
class HistoryMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[HistoryMessage]] = None


class ChatResponse(BaseModel):
    response: str
    resources: list[dict[str, Any]]


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
<<<<<<< HEAD

    response_text = run_agent(_get_agent(), request.message)
    resources = _search_resources(request.message)

    return ChatResponse(response=response_text, resources=resources)
=======
    
    # Convert history to the format the agent expects
    history = []
    if request.history:
        history = [{"role": h.role, "content": h.content} for h in request.history]
    
    response = run_agent(_get_agent(), request.message, history=history)
    return ChatResponse(response=response)
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c
