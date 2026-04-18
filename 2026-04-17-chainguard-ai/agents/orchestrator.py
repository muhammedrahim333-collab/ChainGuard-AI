from __future__ import annotations

from dataclasses import dataclass

from agents.base import BaseChainGuardAgent
from agents.prompts import ORCHESTRATOR_PROMPT


@dataclass
class OrchestratorAgent(BaseChainGuardAgent):
    @classmethod
    def create(cls, settings, memory, llm_service):
        return cls(
            settings=settings,
            memory=memory,
            llm_service=llm_service,
            name="Orchestrator Agent",
            system_prompt=ORCHESTRATOR_PROMPT,
        )

    def summarize_run(self, state: dict) -> str:
        return self.narrate(
            task="Summarize the full supply chain protection cycle for a Punjab SME owner.",
            context=state,
        )
