import os
import json
import requests
from typing import Any, Callable, Dict, Optional


class NemotronNanoClient:
    """Minimal HTTP client wrapper for the Nemotron Nano API.

    Expects environment variables:
    - NEMOTRON_API_URL (e.g. https://api.nemotron.example/v1/generate)
    - NEMOTRON_API_KEY
    """

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url or os.getenv("NEMOTRON_API_URL", "http://localhost:8080/generate")
        self.api_key = api_key or os.getenv("NEMOTRON_API_KEY")

    def call_model(self, prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"prompt": prompt, "temperature": temperature}
        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            # Assume Nemotron returns JSON; be defensive
            return resp.json()
        except Exception:
            return {"error": "nemotron_call_failed", "text": ""}


# --- Simple in-process SJSU 'database' used for RAG ---
SJSU_DB = {
    "parking": "SJSU parking info: permits required Mon-Fri 7am-6pm. Visitor parking at meters and visitor lots.",
    "library": "Dr. Martin Luther King Jr. Library: hours 8am-10pm weekdays, research help at 2nd floor desks.",
    "cs_major": "Computer Science department main office: Engineering Building, Room 123; undergrad advisor contact: cs-advising@sjsu.edu",
    "events": "Today: Campus Career Fair 10am-3pm in Event Center. Spring concert next Friday.",
}


def query_sjsu_database(topic: str) -> str:
    """Tool: Query the SJSU knowledge base. Simple keyword lookup for RAG demos."""
    key = topic.strip().lower()
    return SJSU_DB.get(key, "No direct match found in SJSU DB for that topic.")


def get_campus_events() -> str:
    """Tool: Return upcoming campus events (static demo)."""
    return SJSU_DB.get("events", "No events found.")


class AIResourceAgent:
    """Agent that integrates Nemotron Nano with simple tool calls and RAG.

    Pattern:
      - Receive user question
      - Perform RAG lookup against `query_sjsu_database`
      - Call Nemotron Nano with RAG context included
      - Parse Nemotron response for tool call instructions
      - If a tool is requested, call it and return final answer
      - If Nemotron doesn't return clear tool-call, fall back to helpful campus response
    """

    def __init__(self, model_client: Optional[NemotronNanoClient] = None):
        self.model = model_client or NemotronNanoClient()
        # Tools registry
        self.tools: Dict[str, Callable[..., Any]] = {
            "query_sjsu_database": query_sjsu_database,
            "get_campus_events": lambda: get_campus_events(),
        }

    def rag_lookup(self, question: str) -> str:
        # Basic keyword extraction: look for known topics in question
        for k in SJSU_DB.keys():
            if k in question.lower():
                return SJSU_DB[k]
        return ""

    def _build_prompt(self, question: str, rag_ctx: str) -> str:
        prompt = (
            "You are an assistant for SJSU students. Use the provided context before answering.\n"
            f"Context:\n{rag_ctx}\n---\nQuestion: {question}\n"
            "If you want to call a tool, respond JSON with keys: thought, tool_call (name, args).\n"
            "Otherwise respond with 'final_answer' text in JSON."
        )
        return prompt

    def _parse_model_response(self, resp: Dict[str, Any]) -> Dict[str, Any]:
        # Expect resp to be a dict; flexible parsing for different APIs
        # Try: resp = {"thought":"...","tool_call":{...}} OR resp = {"text":"..."}
        if not isinstance(resp, dict):
            return {"error": "invalid_model_response"}
        # If API returns top-level text field, try to parse JSON inside
        if "text" in resp and resp.get("text"):
            text = resp["text"].strip()
            try:
                return json.loads(text)
            except Exception:
                return {"final_answer": text}
        # Already structured
        return resp

    def run_once(self, question: str) -> str:
        # RAG: retrieve context
        rag_ctx = self.rag_lookup(question)
        prompt = self._build_prompt(question, rag_ctx)
        model_raw = self.model.call_model(prompt)
        parsed = self._parse_model_response(model_raw)

        # If model suggests a tool call
        tool_call = parsed.get("tool_call")
        thought = parsed.get("thought") or parsed.get("reason")

        if tool_call and isinstance(tool_call, dict):
            name = tool_call.get("name")
            args = tool_call.get("args", {}) or {}
            tool = self.tools.get(name)
            if tool:
                try:
                    result = tool(**args) if isinstance(args, dict) else tool(args)
                    final = {
                        "thought": thought or f"Called tool {name}",
                        "tool_result": result,
                        "final_answer": f"I called {name} and found: {result}",
                    }
                    return json.dumps(final)
                except Exception as e:
                    return json.dumps({"error": "tool_failed", "message": str(e)})
            else:
                return json.dumps({"error": "unknown_tool", "tool": name})

        # No explicit tool call -> if model returned final_answer, use it
        if "final_answer" in parsed:
            return parsed["final_answer"]

        # If model returned free text, use it
        if parsed.get("text"):
            return parsed["text"]

        # Fallback: produce helpful campus-related answer using RAG
        if rag_ctx:
            return f"Based on campus info: {rag_ctx}"

        # Generic fallback
        return (
            "I couldn't parse the model response. Here's some helpful campus guidance: "
            + get_campus_events()
        )

    def interact(self) -> None:
        print("SJSU AI Agent — type 'exit' to quit")
        while True:
            q = input("Question: ")
            if not q or q.strip().lower() in ("exit", "quit"):
                break
            print("Thought: checking DB and possibly calling tools...")
            ans = self.run_once(q)
            print("Final Answer:")
            print(ans)


if __name__ == "__main__":
    agent = AIResourceAgent()
    # Example one-off run (non-interactive)
    example_q = "What are the library hours and where is the CS department office?"
    print(agent.run_once(example_q))
