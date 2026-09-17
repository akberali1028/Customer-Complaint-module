# AGENTS.md

Instructions for any AI coding agent (Claude Code, Codex, Cursor, etc.) working in this repo.
Human-readable project background/dos-and-don'ts live in `aivoa-assignment-guide.md` — read that
first for context. This file is the actionable spec: what to build, and which agents to implement.

## Project

AI-assisted Customer Complaint Management System for pharma manufacturing (API/FDF). Two panels:
a "Log Customer Complaint" form and an "AI Complaint Intake Assistant" chat/upload panel that
auto-fills the form and answers questions about the complaint.

## Non-Negotiable Stack

- Frontend: React + Redux (Redux Toolkit is fine)
- Backend: Python + FastAPI
- Agent orchestration: **LangGraph** (`StateGraph`, real nodes/edges — not an ad hoc loop dressed
  up as an "agent")
- LLM: Groq `gemma2-9b-it` as the default model for every node. Fall back to
  `llama-3.3-70b-versatile` only for a node that needs a larger context window or is
  underperforming on `gemma2-9b-it` — don't default to the bigger model everywhere.
- DB: Postgres (or MySQL)
- Font: Google Inter
- No production-grade OCR/document parsing — a naive text extractor for fabricated sample
  PDFs/emails is enough.

## Architecture

```
React/Redux (chat + form UI)
      │  POST /complaints/intake  (raw text | uploaded file)
      ▼
FastAPI endpoint
      │  invokes
      ▼
LangGraph StateGraph  ──►  Groq (gemma2-9b-it / llama-3.3-70b-versatile)
      │  returns structured ComplaintState
      ▼
FastAPI response ──► Redux store ──► form fields populate ──► user saves ──► Postgres/MySQL
```

## Agent Roster (LangGraph nodes to implement)

| # | Agent / Node | Required? | Input | Output |
|---|---|---|---|---|
| 1 | **Intake Router** | Required | raw text / pasted email / uploaded file | input type + routing decision |
| 2 | **Document Parser** | Required | uploaded PDF/DOCX/TXT/EML | plain text |
| 3 | **Field Extraction** | Required | plain complaint text | structured fields matching the form (source, customer, product, strength, batch/lot, mfg date, expiry, qty affected, complaint type, date, description) |
| 4 | **Severity/Priority Assessment** | Required | extracted fields | initial severity + priority |
| 5 | **Completeness Checker** | Bonus | extracted fields | list of missing/ambiguous required fields |
| 6 | **Risk Classification** | Bonus | extracted fields + severity | risk score/category → feeds "AI Copilot Risk Assessment" panel |
| 7 | **Duplicate Detection** | Bonus | extracted fields + past complaints (DB) | possible duplicate matches |
| 8 | **Root Cause Recommendation** | Bonus | extracted fields + description | candidate root cause category |
| 9 | **CAPA Recommendation** | Bonus | root cause + severity | suggested corrective/preventive actions |
| 10 | **Complaint Summary** | Bonus | full state | 2-3 sentence human-readable summary |
| 11 | **Conversational Assistant** | Required | user chat message + current `ComplaintState` | answer, grounded in the complaint already extracted |

Do 1–4 + 11 first (that's the whole core loop from the reference UI). Add bonus nodes (5–10) once
the core loop works end to end — pick 2–3 of them rather than all six; that's enough to satisfy
"bonus features highly appreciated" without overbuilding.

## Suggested State Schema

```python
class ComplaintState(TypedDict):
    raw_input: str
    input_type: Literal["text", "email", "pdf", "docx", "eml"]
    parsed_text: str
    extracted_fields: dict          # form fields
    completeness_flags: list[str]
    severity: str
    priority: str
    risk_assessment: dict | None
    duplicate_matches: list[dict]
    root_cause: str | None
    capa_suggestions: list[str]
    summary: str | None
    chat_history: list[dict]
```

## Suggested Graph Wiring

```
intake_router
    ├─(file)→ document_parser ─┐
    └─(text/email)─────────────┴→ field_extraction
                                        ├→ severity_assessment
                                        ├→ completeness_checker        (bonus, parallel)
                                        ├→ risk_classification         (bonus, parallel)
                                        ├→ duplicate_detection         (bonus, parallel)
                                        └→ root_cause_recommendation → capa_recommendation (bonus)
                                                                              │
                                                                              ▼
                                                                          summary (bonus)
                                                                              │
                                                                              ▼
                                                                             END
```
`conversational_assistant` is invoked separately from the chat endpoint, reading the persisted
`ComplaintState` for whichever complaint is open — it isn't part of the intake graph's main path.

## Rules for Any Coding Agent Editing This Repo

- Use LangGraph's actual primitives (`StateGraph`, nodes, conditional edges). No hand-rolled
  if/else chain masquerading as "the agent framework."
- Every node must be independently explainable — the developer has to defend each one in an
  interview, so no opaque one-shot mega-prompts doing five jobs at once.
- Don't touch the mandated stack (React/Redux, FastAPI, LangGraph, Groq, Postgres/MySQL) even if
  a substitution would be faster to scaffold.
- Match the *behavior* shown in the reference demo video, not the exact pixel layout.
- Don't implement real OCR/production document parsing — out of scope by spec.

## Setup / Test Commands

*(Fill in once the repo is scaffolded — placeholders below)*

- Backend: `cd backend && uvicorn main:app --reload`
- Frontend: `cd frontend && npm run dev`
- Tests: TBD
