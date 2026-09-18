from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import ConfigDict, BaseModel

from .llm import DEFAULT_MODEL, FALLBACK_MODEL, structured_completion
from .models import FieldUpdate, RiskAssessment


class ChatPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: str
    updates: list[FieldUpdate]


class ChatState(TypedDict, total=False):
    message: str
    fields: dict[str, str | None]
    risk_assessment: dict[str, str]
    answer: str
    updates: list[dict[str, str]]
    reassess: bool
    updated_risk_assessment: dict[str, str]


CHAT_PROMPT = """You are Aivoa AI, a grounded pharma complaint intake assistant. Answer only from
the current complaint context. If the user explicitly asks to change a complaint detail, return
only the requested field updates and preserve every other field. Do not infer extra edits. If the
user asks a question, return an answer and no updates. This is an intake aid, not a final QA decision."""

RISK_PROMPT = """You are a pharma quality intake triage assistant, not a final QA decision maker.
Return a conservative initial severity, priority, suggested action, and concise risk rationale using
only the supplied fields. Escalate potential patient safety, contamination, mix-up, tampering,
sterility, or broad batch-impact issues. Return schema-compliant JSON."""

RISK_RELEVANT_FIELDS = {
    "product_name", "product_strength_grade", "batch_lot_number", "quantity_affected",
    "complaint_type", "detailed_complaint_description",
}


async def conversational_assistant(state: ChatState) -> ChatState:
    context = f"Current complaint fields: {state['fields']}\nCurrent risk: {state['risk_assessment']}\nUser message: {state['message']}"
    plan = await structured_completion(system_prompt=CHAT_PROMPT, user_prompt=context, schema=ChatPlan, model=DEFAULT_MODEL)
    updates = [item.model_dump() for item in plan.updates]
    return {"answer": plan.answer, "updates": updates, "reassess": any(item["field_name"] in RISK_RELEVANT_FIELDS for item in updates)}


def should_reassess(state: ChatState) -> Literal["reassess", "end"]:
    return "reassess" if state.get("reassess") else "end"


async def risk_reassessment(state: ChatState) -> ChatState:
    fields = dict(state["fields"])
    for update in state["updates"]:
        fields[update["field_name"]] = update["value"]
    risk = await structured_completion(system_prompt=RISK_PROMPT, user_prompt=str(fields), schema=RiskAssessment, model=FALLBACK_MODEL)
    return {"updated_risk_assessment": risk.model_dump()}


def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("conversational_assistant", conversational_assistant)
    graph.add_node("risk_reassessment", risk_reassessment)
    graph.add_edge(START, "conversational_assistant")
    graph.add_conditional_edges("conversational_assistant", should_reassess, {"reassess": "risk_reassessment", "end": END})
    graph.add_edge("risk_reassessment", END)
    return graph.compile()


chat_graph = build_chat_graph()
