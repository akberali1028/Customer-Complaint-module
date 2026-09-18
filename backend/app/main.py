from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .graph import intake_graph
from .chat_graph import chat_graph
from .db import save_complaint
from .models import ChatRequest, ChatResponse, IntakeRequest, IntakeResponse, SaveComplaintRequest, SaveComplaintResponse
from .parser import input_type_for_filename

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


@app.post("/api/complaints/intake-file", response_model=IntakeResponse)
async def intake_file(file: UploadFile = File(...)) -> IntakeResponse:
    try:
        input_type = input_type_for_filename(file.filename or "")
        content = await file.read()
        if not content:
            raise ValueError("The uploaded file is empty.")
        if len(content) > 5 * 1024 * 1024:
            raise ValueError("The maximum file size is 5 MB.")
        state = await intake_graph.ainvoke({"raw_input": "", "input_type": input_type, "file_content": content})
        return IntakeResponse(input_type=state["input_type"], fields=state["extracted_fields"], risk_assessment=state["risk_assessment"], used_fallback_model=state["used_fallback_model"], missing_fields=state.get("missing_fields", []))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI file intake failed: {exc}") from exc


@app.post("/api/complaints/chat", response_model=ChatResponse)
async def chat_about_complaint(request: ChatRequest) -> ChatResponse:
    try:
        state = await chat_graph.ainvoke({"message": request.message, "fields": request.fields.model_dump(), "risk_assessment": request.risk_assessment.model_dump()})
        return ChatResponse(answer=state["answer"], updates=state["updates"], risk_assessment=state.get("updated_risk_assessment"))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI assistant failed: {exc}") from exc


@app.post("/api/complaints", response_model=SaveComplaintResponse)
async def save_reviewed_complaint(request: SaveComplaintRequest) -> SaveComplaintResponse:
    try:
        complaint_id = save_complaint(request.fields.model_dump(), request.risk_assessment.model_dump())
        return SaveComplaintResponse(id=complaint_id, message="Complaint saved to the QMS ledger.")
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database save failed: {exc}") from exc
