from __future__ import annotations

from pydantic import BaseModel


class SupplierRiskAssessment(BaseModel):
    supplier_id: str
    supplier_name: str
    risk_score: int
    severity_label: str
    reasoning: list[str]
    delay_probability: float
    profit_impact_inr: float
