from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ComplaintFields(BaseModel):
    complaint_source: str | None = None
    customer_name: str | None = None
    product_name: str | None = None
    product_strength_grade: str | None = None
    batch_lot_number: str | None = None
    manufacturing_date: str | None = None
    expiry_date: str | None = None
    quantity_affected: str | None = None
    complaint_type: str | None = None
    complaint_date: str | None = None
    detailed_complaint_description: str | None = None


class RiskAssessment(BaseModel):
    severity_suggested: Literal["Minor", "Major", "Critical"]
    priority: Literal["Low", "Medium", "High", "Urgent"]
    suggested_next_action: str
    initial_risk_assessment: str


class IntakeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=30_000)


class IntakeResponse(BaseModel):
    input_type: Literal["text", "email"]
    fields: ComplaintFields
    risk_assessment: RiskAssessment
    used_fallback_model: bool
    missing_fields: list[str]
