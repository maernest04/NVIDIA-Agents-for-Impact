import json
import sqlite3

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from backend.config import settings
from backend.database import DB_PATH

# Nano model for fast sub-calls inside tools — keeps latency acceptable
# while still using Nemotron for genuine reasoning.
_SUB_MODEL = "nvidia/nemotron-3-nano-30b-a3b"


def _reasoning_llm() -> ChatNVIDIA:
    return ChatNVIDIA(
        model=_SUB_MODEL,
        api_key=settings.nemotron_api_key,
        base_url=settings.nemotron_base_url,
        temperature=0.1,
    )


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _rows_to_text(rows) -> str:
    if not rows:
        return "No matching resources found."
    parts = []
    for r in rows:
        lines = [f"**{r['resource_name']}**", f"Phone: {r['phone_number']}"]
        if r["email"] and r["email"] != "N/A":
            lines.append(f"Email/Text: {r['email']}")
        lines.append(r["description"])
        parts.append("\n".join(lines))
    return "\n\n---\n\n".join(parts)


# ---------------------------------------------------------------------------
# Tool 1: Urgency assessment — Nemotron reasons about risk level
# ---------------------------------------------------------------------------

_URGENCY_SYSTEM = """\
You are a crisis assessment specialist trained to evaluate the urgency of \
messages from students and community members seeking help.

Analyze the message and return ONLY a valid JSON object with exactly these fields:

{
  "urgency": "immediate" | "elevated" | "standard",
  "reason": "one sentence explaining your assessment",
  "action": "what the main agent should do next"
}

Urgency definitions:
- "immediate": any indication of suicidal ideation, intent to self-harm, \
  active physical danger, ongoing assault, or life-threatening emergency. \
  This includes indirect expressions like "I don't want to be here anymore", \
  "everyone would be better off without me", or "I can't take it anymore" when \
  combined with despair. When in doubt, err on the side of immediate.
- "elevated": abuse, domestic violence, assault (past or ongoing), \
  homelessness or imminent eviction, substance use crisis, or serious \
  distress that needs urgent but non-emergency response.
- "standard": academic stress, career concerns, general mental health support, \
  financial aid questions, accessibility needs, or informational requests.

Return ONLY the JSON. No explanation, no markdown, no extra text.\
"""


@tool
def assess_urgency(message: str) -> str:
    """Use Nemotron to reason about the urgency level of the user's message.

    ALWAYS call this tool FIRST, before any other tool, for every message.
    Nemotron evaluates the message for indicators of immediate risk, serious
    distress, or general need — and returns a structured urgency assessment
    that guides which tools to call next.
    """
    llm = _reasoning_llm()
    response = llm.invoke([
        SystemMessage(content=_URGENCY_SYSTEM),
        HumanMessage(content=f"Assess this message:\n\n{message}"),
    ])

    try:
        # Strip markdown code fences if the model wraps its output
        raw = response.content.strip().strip("```json").strip("```").strip()
        result = json.loads(raw)
        # Validate expected keys are present
        if "urgency" not in result:
            raise ValueError("missing urgency key")
        return json.dumps(result)
    except Exception:
        # Safe fallback — never crash on a safety-critical tool
        return json.dumps({
            "urgency": "elevated",
            "reason": "Could not parse assessment; defaulting to elevated for safety.",
            "action": "Call triage_situation next, then search_resources.",
        })


# ---------------------------------------------------------------------------
# Tool 2: Situation triage — Nemotron identifies resource categories
# ---------------------------------------------------------------------------

_TRIAGE_SYSTEM = """\
You are a student support specialist at San Jose State University. \
Your job is to analyze a student or community member's message and determine \
which support categories and resources are most relevant to their situation.

Return ONLY a valid JSON object with exactly these fields:

{
  "identified_categories": ["category1", "category2"],
  "recommended_searches": ["search term 1", "search term 2"],
  "primary_resource": "name of the single most important resource to find",
  "instruction": "brief instruction for the agent on what to search"
}

Available resource categories (use only what applies):
- mental health → search: "counseling", "CAPS", "mental health"
- basic needs / financial → search: "financial aid", "SJSU Cares", "food"
- housing → search: "housing", "SJSU Cares"
- academic support → search: "writing center", "academic", "registrar"
- career → search: "career center", "career"
- LGBTQ+ support → search: "PRIDE", "gender equity"
- immigration / international → search: "ISSS", "international", "UndocuSpartan"
- veterans → search: "veteran", "Veterans Crisis Line"
- safety / domestic violence → search: "domestic violence", "UPD"
- accessibility → search: "Accessible Education Center"
- crisis / general → search: "SJSU Cares", "counseling", "988"

Return ONLY the JSON. No explanation, no markdown, no extra text.\
"""


@tool
def triage_situation(user_message: str) -> str:
    """Use Nemotron to analyze the user's situation and identify the right resource categories.

    Call this after assess_urgency returns 'elevated' or 'standard'.
    Nemotron reasons about the user's needs and returns structured categories
    and search terms to guide the resource lookup in search_resources.
    """
    llm = _reasoning_llm()
    response = llm.invoke([
        SystemMessage(content=_TRIAGE_SYSTEM),
        HumanMessage(content=f"Triage this situation:\n\n{user_message}"),
    ])

    try:
        raw = response.content.strip().strip("```json").strip("```").strip()
        result = json.loads(raw)
        if "recommended_searches" not in result:
            raise ValueError("missing recommended_searches key")
        return json.dumps(result)
    except Exception:
        return json.dumps({
            "identified_categories": ["general support"],
            "recommended_searches": ["SJSU Cares", "counseling"],
            "primary_resource": "SJSU Cares",
            "instruction": "Search for SJSU Cares and counseling resources.",
        })


# ---------------------------------------------------------------------------
# Tool 3: DB resource lookup
# ---------------------------------------------------------------------------

@tool
def search_resources(query: str) -> str:
    """Search SJSU campus resources and national crisis hotlines by keyword.

    Use this after triage_situation identifies categories.
    Searches both resource names and descriptions.
    Returns matching resources with phone numbers and descriptions.
    """
    con = _db()
    rows = con.execute(
        """
        SELECT resource_name, phone_number, email, description
        FROM campus_resources
        WHERE resource_name LIKE ? OR description LIKE ?
        """,
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    con.close()
    return _rows_to_text(rows)


@tool
def get_resource_by_name(name: str) -> str:
    """Retrieve a specific campus resource or hotline by its exact or partial name.

    Use this when you already know the name of the resource, such as
    'CAPS', 'SJSU Cares', '988', 'PRIDE Center', etc.
    """
    con = _db()
    row = con.execute(
        "SELECT resource_name, phone_number, email, description FROM campus_resources WHERE resource_name LIKE ?",
        (f"%{name}%",),
    ).fetchone()
    con.close()
    if not row:
        return f"No resource found matching '{name}'."
    return _rows_to_text([row])


# ---------------------------------------------------------------------------
# Tool 4: Draft outreach message — Nemotron generates personalized text
# ---------------------------------------------------------------------------

_DRAFT_SYSTEM = """\
You are a compassionate student advocate helping an SJSU student reach out for support.
Write two things based on their situation:

1. A ready-to-send EMAIL (warm, concise, 3–4 sentences max)
2. A PHONE SCRIPT (2–3 sentences they can read aloud when they call)

Format your response EXACTLY like this:

**EMAIL DRAFT**
Subject: [subject line]

[email body — use [Your Name] and [Student ID – optional] as placeholders]

---

**WHEN YOU CALL**
[phone script — conversational, first-person, warm tone]

Rules:
- Never be clinical or cold. Write like a caring advisor.
- Keep both sections brief — students are often in distress and need clarity.
- The email subject should be specific but not expose sensitive details.
- Do NOT add any other sections or commentary outside this format.\
"""


@tool
def draft_outreach_message(resource_name: str, user_situation: str) -> str:
    """Use Nemotron to draft a personalized, empathetic email and phone script.

    Call this as the FINAL step (after searching for resources) for non-immediate situations.
    Nemotron generates contextually aware outreach text based on the student's specific situation.
    Do NOT call this for immediate/emergency situations — focus on 988/911 instead.
    """
    llm = _reasoning_llm()
    prompt = (
        f"The student needs to contact: **{resource_name}**\n\n"
        f"Their situation: {user_situation[:300]}"
    )
    response = llm.invoke([
        SystemMessage(content=_DRAFT_SYSTEM),
        HumanMessage(content=prompt),
    ])
    return response.content
