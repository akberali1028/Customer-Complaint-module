from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from .llm import DEFAULT_MODEL, FALLBACK_MODEL, structured_completion
from .models import ComplaintFields, RiskAssessment


class ComplaintState(TypedDict, total=False):
    raw_input: str
    input_type: Literal["text", "email"]
    parsed_text: str
    extracted_fields: dict[str, str | None]
    missing_fields: list[str]
    risk_assessment: dict[str, str]
    extraction_needs_fallback: bool
    used_fallback_model: bool


FIELD_EXTRACTION_PROMPT = """You extract a pharma customer complaint into the provided schema.
Use only facts stated or plainly implied in the complaint. Do not invent a customer, lot, dates,
or quantity. Use null for unknown values. Put the reported issue in detailed_complaint_description.
The output must match the JSON schema exactly."""

RISK_PROMPT = """You are a pharma quality intake triage assistant, not a final QA decision maker.
Based only on the extracted complaint fields, return an initial suggested severity, priority, next
action, and concise risk rationale. Escalate potential patient safety, contamination, mix-up,
tampering, sterility, or broad batch-impact issues. Avoid regulatory claims and state uncertainty
when facts are missing. The output must match the JSON schema exactly."""

CRITICAL_EXTRACTION_FIELDS = (
    "product_name",
    "batch_lot_number",
    "complaint_type",
    "detailed_complaint_description",
)


def intake_router(state: ComplaintState) -> ComplaintState:
    text = state["raw_input"].strip()
    is_email = "\nfrom:" in text.lower() or "\nsubject:" in text.lower()
    return {"input_type": "email" if is_email else "text", "parsed_text": text}


async def field_extraction(state: ComplaintState) -> ComplaintState:
    fields = await structured_completion(
        system_prompt=FIELD_EXTRACTION_PROMPT,
        user_prompt=state["parsed_text"],
        schema=ComplaintFields,
        model=DEFAULT_MODEL,
    )
    field_data = fields.model_dump()
    missing = [name for name in CRITICAL_EXTRACTION_FIELDS if not field_data.get(name)]
    return {
        "extracted_fields": field_data,
        "missing_fields": missing,
        "extraction_needs_fallback": bool(missing),
        "used_fallback_model": False,
    }


def needs_fallback(state: ComplaintState) -> Literal["fallback", "assessment"]:
    return "fallback" if state.get("extraction_needs_fallback") else "assessment"


async def extraction_fallback(state: ComplaintState) -> ComplaintState:
    fields = await structured_completion(
        system_prompt=FIELD_EXTRACTION_PROMPT,
        user_prompt=state["parsed_text"],
        schema=ComplaintFields,
        model=FALLBACK_MODEL,
    )
    field_data = fields.model_dump()
    missing = [name for name in CRITICAL_EXTRACTION_FIELDS if not field_data.get(name)]
    return {
        "extracted_fields": field_data,
        "missing_fields": missing,
        "used_fallback_model": True,
    }


async def severity_priority_assessment(state: ComplaintState) -> ComplaintState:
    assessment = await structured_completion(
        system_prompt=RISK_PROMPT,
        user_prompt=str(state["extracted_fields"]),
        schema=RiskAssessment,
        model=DEFAULT_MODEL,
    )
    return {"risk_assessment": assessment.model_dump()}


def build_intake_graph():
    graph = StateGraph(ComplaintState)
    graph.add_node("intake_router", intake_router)
    graph.add_node("field_extraction", field_extraction)
    graph.add_node("extraction_fallback", extraction_fallback)
    graph.add_node("severity_priority_assessment", severity_priority_assessment)
    graph.add_edge(START, "intake_router")
    graph.add_edge("intake_router", "field_extraction")
    graph.add_conditional_edges(
        "field_extraction",
        needs_fallback,
        {"fallback": "extraction_fallback", "assessment": "severity_priority_assessment"},
    )
    graph.add_edge("extraction_fallback", "severity_priority_assessment")
    graph.add_edge("severity_priority_assessment", END)
    return graph.compile()


intake_graph = build_intake_graph()
