from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .graph import intake_graph
from .models import IntakeRequest, IntakeResponse

app = FastAPI(title="Aivoa AI Complaint Intake API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/complaints/intake", response_model=IntakeResponse)
async def intake_complaint(request: IntakeRequest) -> IntakeResponse:
    try:
        state = await intake_graph.ainvoke({"raw_input": request.text})
        return IntakeResponse(
            input_type=state["input_type"],
            fields=state["extracted_fields"],
            risk_assessment=state["risk_assessment"],
            used_fallback_model=state["used_fallback_model"],
            missing_fields=state.get("missing_fields", []),
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI intake failed: {exc}") from exc
