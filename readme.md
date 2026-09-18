# Aivoa AI Complaint Intake

A lightweight customer-complaint intake and triage workflow for pharma API/FDF manufacturing.
The user provides complaint text to Aivoa AI; the LangGraph workflow extracts the required
details, suggests an initial assessment, and auto-populates the review form. Manual field entry
is not part of the primary demo flow.

## Current scope

- React + Vite + Redux Toolkit frontend with the fields shown in the assignment reference.
- FastAPI + LangGraph backend for text intake.
- Groq `openai/gpt-oss-20b` handles routing, extraction, and conversational edits. It retries
  invalid structured extraction with `openai/gpt-oss-120b`; all severity/priority and risk
  assessments use 120B for higher-confidence triage.
- PDF/DOCX/TXT/EML intake, follow-up AI edits, risk reassessment, and PostgreSQL saving are included.

## Local setup

Create `.env` in the repository root (it is ignored by Git):

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql+psycopg://aivoa:aivoa@localhost:5432/aivoa
```

`Project_key` is also accepted temporarily to support the existing local environment file, but
`GROQ_API_KEY` is the preferred name.

Start the backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Start PostgreSQL first:

```powershell
docker compose up -d postgres
```

In another terminal, start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). The frontend proxies `/api` to FastAPI.

## First demo prompt

> Apollo Pharmacy reported discolored capsules in Amoxicillin Capsules 500 mg. Batch number
> AMX240602. Manufacturing date March 2026. Expiry date February 2028. Please log this complaint.

The expected result is a populated complaint form plus suggested severity, next action, and risk
assessment. The user reviews the AI result before saving it to the QMS ledger.

## Assistant actions

- Upload a text-based PDF, DOCX, TXT, or EML file (maximum 5 MB) to use the same intake graph.
- Ask an edit such as `change strength to 1000 mg`; only that field changes. Risk is recalculated
  only when the edit can affect triage.
- Select **Save Complaint** after review to save the full AI-populated record to Postgres.
