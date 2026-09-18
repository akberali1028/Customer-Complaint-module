from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ComplaintFields(StrictModel):
    complaint_source: str | None
    customer_name: str | None
    product_name: str | None
    product_strength_grade: str | None
    batch_lot_number: str | None
    manufacturing_date: str | None
    expiry_date: str | None
    quantity_affected: str | None
    complaint_type: str | None
    complaint_date: str | None
    detailed_complaint_description: str | None


class RiskAssessment(StrictModel):
    severity_suggested: Literal["Minor", "Major", "Critical"]
    priority: Literal["Low", "Medium", "High", "Urgent"]
    suggested_next_action: str
    initial_risk_assessment: str


class IntakeRequest(StrictModel):
    text: str = Field(min_length=1, max_length=30_000)


class IntakeResponse(StrictModel):
    input_type: Literal["text", "email", "pdf", "docx", "txt", "eml"]
    fields: ComplaintFields
    risk_assessment: RiskAssessment
    used_fallback_model: bool
    missing_fields: list[str]


class ChatRequest(StrictModel):
    message: str = Field(min_length=1, max_length=10_000)
    fields: ComplaintFields
    risk_assessment: RiskAssessment


class FieldUpdate(StrictModel):
    field_name: Literal[
        "complaint_source", "customer_name", "product_name", "product_strength_grade",
        "batch_lot_number", "manufacturing_date", "expiry_date", "quantity_affected",
        "complaint_type", "complaint_date", "detailed_complaint_description",
    ]
    value: str


class ChatResponse(StrictModel):
    answer: str
    updates: list[FieldUpdate]
    risk_assessment: RiskAssessment | None = None


class SaveComplaintRequest(StrictModel):
    fields: ComplaintFields
    risk_assessment: RiskAssessment


class SaveComplaintResponse(StrictModel):
    id: int
    message: str
