from __future__ import annotations

from dataclasses import dataclass

from agents.base import BaseChainGuardAgent
from agents.prompts import MITIGATION_PROMPT


@dataclass
class MitigationAgent(BaseChainGuardAgent):
    @classmethod
    def create(cls, settings, memory, llm_service):
        return cls(
            settings=settings,
            memory=memory,
            llm_service=llm_service,
            name="Mitigation Agent",
            system_prompt=MITIGATION_PROMPT,
        )

    def run(self, suppliers, assessments, disruption_hint: str = "") -> dict:
        mitigations = {}
        for supplier in suppliers:
            assessment = assessments[supplier.supplier_id]
            if assessment.risk_score < 35:
                steps = [
                    "Normal monitoring continue rakho, no immediate supplier switch needed.",
                    "Reconfirm dispatch ETA within 24 hours.",
                    "Keep 1 small backup quotation ready for contingency.",
                ]
            else:
                steps = [
                    f"Immediate alternate sourcing evaluate karo for {supplier.product} within Punjab or nearby NCR.",
                    "Dispatch buffer stock for 5 to 7 days if finished-goods orders are at risk.",
                    f"Route options re-check karo because {supplier.city} may face logistics disruption.",
                    "MSME or export-linked scheme/support eligibility review karo for working-capital pressure.",
                    "Daily supplier check-in and updated ETA lock karo till risk cools down.",
                ]
            if disruption_hint:
                steps.insert(0, f"Disruption match detected: {disruption_hint}. Act before next shipment window.")
            memory_tip = self.memory.reflect(
                f"What mitigation worked earlier for disruptions like {disruption_hint or assessment.severity_label}?"
            )
            mitigations[supplier.supplier_id] = {
                "supplier": supplier.name,
                "severity": assessment.severity_label,
                "actions": steps[:5],
                "memory_hint": memory_tip,
            }
        return mitigations
