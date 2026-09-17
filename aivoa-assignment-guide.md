# AIVOA Round 1 — AI Product Engineer Intern Assignment

**Project:** AI-Powered Customer Complaint Management System (pharma manufacturing — API & FDF)
**Company:** aivoa.ai

---

## 1. Project Context

Pharma manufacturers run a **QMS (Quality Management System)**. One module of that is
**Customer Complaint Management** — when a customer (or regulator) reports a defect/issue with
a batch of API (Active Pharmaceutical Ingredient) or FDF (Finished Dosage Form), the complaint
has to be logged, triaged, investigated, and tracked (often feeding into **CAPA** — Corrective
and Preventive Action). This assignment asks you to build a lightweight, AI-assisted version of
that intake + triage workflow — not a full QMS.

**What the reference UI shows** (from the provided screenshot):
- **Left panel — "Log Customer Complaint" form**, with 4 sections:
  1. Origin & Customer Details (complaint source, customer name)
  2. Product & Batch Identification (product name/strength, batch/lot #, mfg/expiry date, qty affected)
  3. Complaint Details (type, date, description)
  4. Initial Assessment & Priority (severity, priority)
  Fields start as "Awaiting AI extraction…" placeholders and get filled in automatically.
- **Right panel — "AI Complaint Intake Assistant"**: drag-and-drop a complaint doc (PDF/DOCX/TXT/EML)
  or paste complaint text/email, shows an extraction progress bar, and has a chat box so you can
  ask follow-up questions about the complaint.
- There's also an **"AI Copilot Risk Assessment"** panel mentioned in the deliverables section that
  isn't fully visible in the static screenshot — check the demo video for how it's laid out.

**Core loop:** user gives input (text/PDF/email) → AI extracts structured fields → form
auto-populates → user reviews/edits → save → (optionally) AI does risk classification /
other bonus analysis on top.

---

## 2. Mandatory Tech Stack

| Layer | Requirement |
|---|---|
| Frontend | React + **Redux** for state management |
| Backend | Python + **FastAPI** |
| AI orchestration | **LangGraph** (agent framework) |
| LLM | Groq — **gemma2-9b-it** (primary); `llama-3.3-70b-versatile` allowed "for context" |
| Database | MySQL or Postgres |
| Font | Google Inter |
| Coding tools | Gemini 2.5 Pro (free trial) or ChatGPT 5.0 — or Claude/Copilot/Cursor/Windsurf — all allowed and encouraged |

No pypdf/production OCR needed — you can fabricate realistic sample complaint PDFs/emails/images yourself.

---

## 3. How the Pipeline Should Work

1. **Input** — user pastes text/email or uploads a PDF/DOCX/TXT/EML in the chat-style right panel.
2. **Frontend → API** — React sends the raw input to a FastAPI endpoint.
3. **Backend → LangGraph** — FastAPI triggers a LangGraph graph: nodes for parsing, field
   extraction, maybe completeness-check / risk-classification, etc. Groq (gemma2-9b-it) does the
   actual LLM calls inside the graph.
4. **Response → Redux → Form** — structured JSON comes back, Redux store updates, the "Log
   Customer Complaint" form fields populate (replacing "Awaiting AI extraction…").
5. **Persistence** — on "Save Complaint," data goes into MySQL/Postgres.
6. **(Bonus)** — risk score / duplicate check / CAPA suggestion / summary shown alongside.

---

## 4. Do's

- [ ] Watch the full demo video *before* writing any code.
- [ ] Spend 30–60 min researching QMS + the Customer Complaint module — they explicitly say
      they're grading **curiosity and research**, not domain expertise.
- [ ] Match the **demonstrated functionality** from the video — the UI does *not* need to be pixel-identical.
- [ ] Build a flexible ingestion layer: text paste, PDF, and email should all funnel into the same
      LangGraph pipeline (don't hardcode for just one input type).
- [ ] Fabricate a handful of realistic pharma complaint documents (PDF/email/image) for your demo.
- [ ] Actually **read and understand** any AI-generated code before committing it — you'll be
      asked to explain/modify it live in the interview.
- [ ] Rehearse walking through the full path out loud: frontend input → API endpoint → backend →
      LangGraph/AI → response → form population. This is explicitly what the code-walkthrough
      video (and the interview) will probe.
- [ ] Implement at least one or two bonus features (Completeness Checker, Root Cause
      Recommendation, Duplicate Detection, CAPA Recommendation, Summary, Risk Classification) —
      they're "highly appreciated," i.e. a real differentiator among submissions.
- [ ] Record **two videos** (5–10 min each): one product demo, one code walkthrough — both required.
- [ ] Submit GitHub repo + both videos via the provided Google Form.

## 5. Don'ts

- [ ] Don't copy-paste AI-generated code you can't explain — this is stated twice in the doc and
      will surface directly in the interview.
- [ ] Don't swap out any part of the mandatory stack (React/Redux, FastAPI, LangGraph, Groq,
      MySQL/Postgres) for something more familiar, even if it'd be faster to build.
- [ ] Don't over-invest time pixel-matching the reference screenshot — functionality > visuals.
- [ ] Don't attempt real/production-grade OCR or document parsing — explicitly out of scope.
- [ ] Don't skip the CAPA/QMS context step to jump straight to code — it likely affects how the
      "Initial Assessment & Priority" fields and severity logic should behave realistically.
- [ ] Don't submit something you can't defend — they'll ask you to modify/extend it in the interview.

---

## 6. Things to Be Careful About (Risk Areas for You Specifically)

- **LangGraph is new territory.** No hands-on LangChain/CrewAI/N8N experience yet, so budget
  real learning time here — LangGraph's node/edge/state-graph mental model is a bit different from
  a plain LLM call. Do the official quickstart first before wiring it into this project.
- **Redux may be heavier than the React state you've used before** (e.g. the macro keyboard
  configurator). Redux Toolkit (RTK) cuts a lot of the boilerplate and still satisfies "Redux for
  state management" — worth using unless the brief specifically wants raw Redux.
- **FastAPI** — you're already learning this from scratch via a CRUD tutorial; use this project as
  your real practice reps rather than something to route around.
- **Groq/gemma2-9b-it reliability for agentic/tool-calling steps** — smaller/faster models can be
  flakier at structured extraction or multi-step tool use than larger ones; test extraction
  accuracy early, and keep `llama-3.3-70b-versatile` in your back pocket for tougher extraction
  steps if gemma2-9b-it underperforms (the spec explicitly allows this).
- **"AI Copilot Risk Assessment" panel** isn't clearly shown in the static reference screenshot —
  confirm its exact layout/behavior from the demo video before building it.
- **Deadline isn't stated in the extracted assignment text** — double-check the submission
  deadline wherever you received this doc (email/portal), since it's not in the doc itself.
