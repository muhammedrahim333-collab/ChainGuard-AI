from __future__ import annotations

from dataclasses import dataclass

from agents.base import BaseChainGuardAgent
from agents.prompts import PREDICTOR_PROMPT
from tools.risk import RiskScoringTool


@dataclass
class RiskPredictorAgent(BaseChainGuardAgent):
    risk_tool: RiskScoringTool

    @classmethod
    def create(cls, settings, memory, llm_service):
        return cls(
            settings=settings,
            memory=memory,
            llm_service=llm_service,
            name="Risk Predictor Agent",
            system_prompt=PREDICTOR_PROMPT,
            risk_tool=RiskScoringTool(),
        )

    def run(self, suppliers, monitor_output, disruption_hint: str = "") -> dict:
        assessments = {}
        for supplier in suppliers:
            signals = monitor_output.get(supplier.supplier_id, {})
            assessment = self.risk_tool.score_supplier(
                supplier=supplier,
                signals=signals,
                disruption_hint=disruption_hint,
            )
            reflection = self.memory.reflect(
                f"What should ChainGuard AI remember about supplier {supplier.name} and similar risk patterns?"
            )
            assessment.reasoning.append(reflection)
            assessments[supplier.supplier_id] = assessment
        return assessments
