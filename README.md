# SJSU Safeline

**NVIDIA Agents for Impact Hackathon** — A compassionate AI agent that helps SJSU students find the right campus or national resource when they're embarrassed or nervous to reach out. No judgment; describe your situation in your own words and get a specific contact plus a message you can send or say.

---

## What it does

- **Multi-stage reasoning:** The agent doesn’t just answer — it assesses urgency, triages your situation, searches the resource database, and drafts a personalized outreach message (email + phone script) using **NVIDIA Nemotron**.
- **SJSU + nationwide:** 33 campus resources (CAPS, SJSU Cares, PRIDE Center, ISSS, AEC, etc.) and 13 national hotlines (988, Crisis Text Line, Trevor Project, NDVH, RAINN, SAMHSA, Veterans Crisis Line, and more).
- **Visible decision-making:** The **Agent Trace** panel shows the real tool chain (urgency → triage → search → draft) so you can see the agent thinking, planning, and acting.

---

## Tech stack

| Layer   | Stack |
|--------|--------|
| **LLM / Agent** | NVIDIA Nemotron (super-120b orchestrator + nano-30b for tool sub-calls) via `langchain-nvidia-ai-endpoints` |
| **Backend**     | FastAPI, LangChain (tool-calling agent), SQLite |
| **Frontend**    | React, Vite, Tailwind CSS |
| **Streaming**  | Server-Sent Events (SSE) for real-time response and tool-call events |

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **NVIDIA API key** for [NVIDIA NIM / Nemotron](https://build.nvidia.com/)

---

## Setup

### 1. Environment

At the **project root**, create a `.env` file:

```env
NEMOTRON_API_KEY=your-nvidia-api-key
NEMOTRON_BASE_URL=https://integrate.api.nvidia.com/v1
```

### 2. Seed the resource database (one-time)

From the project root:

```bash
cd backend/data && python seed.py && cd ../..
```

This creates `backend/data/campus_resources.db` with 46 campus and national resources.

### 3. Backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Frontend dependencies

```bash
cd fe && npm install && cd ..
```

---

## Run

**Terminal 1 — Backend (from project root):**

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd fe && npm run dev
```

Open **http://localhost:5173**. The Vite dev server proxies `/chat/` and `/resources/` to the backend at port 8000.

---

## Agent workflow

1. **Assess urgency** — Nemotron evaluates the message (immediate / elevated / standard). If immediate, the agent responds with 988/911 and stops.
2. **Triage situation** — Nemotron identifies resource categories and search terms (e.g. mental health, SJSU Cares, LGBTQ+).
3. **Search resources** — SQLite lookup by keyword and/or by resource name (e.g. CAPS, 988).
4. **Draft outreach** — Nemotron generates a short, empathetic email draft and phone script tailored to the student’s situation.

All of this is visible in the **Agent Trace** panel (top-right) during and after each reply.

---

## Project structure

```
NVIDIA-Agents-for-Impact/
├── .env                    # NEMOTRON_API_KEY, NEMOTRON_BASE_URL (create this)
├── requirements.txt        # Python deps
├── backend/
│   ├── main.py             # FastAPI app, CORS, routers
│   ├── config.py           # Settings (loads .env from repo root)
│   ├── database.py          # SQLite path and get_db
│   ├── agent/
│   │   ├── agent.py        # LangChain tool-calling agent, run_agent(), ToolCallCollector
│   │   └── tools.py        # assess_urgency, triage_situation, search_resources, get_resource_by_name, draft_outreach_message
│   ├── routers/
│   │   ├── chat.py         # POST /chat/ — SSE stream (tool_call, categories, token, done)
│   │   ├── health.py       # GET /health
│   │   └── resources.py    # GET /resources/, GET /resources/{id}
│   └── data/
│       ├── seed.py         # Builds campus_resources.db
│       └── campus_resources.db
└── fe/                     # React + Vite + Tailwind
    ├── src/
    │   ├── App.jsx         # Chat state, SSE handling, agentTrace
    │   ├── api.js          # sendChatMessage (SSE), fetchResources
    │   └── components/     # ChatLayout, ChatMessage, ChatInput, Header, AgentTrace, ResourceCard
    └── package.json
```

---

## License

MIT.
