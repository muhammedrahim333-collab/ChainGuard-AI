from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import Settings
from memory.hindsight import HindsightMemoryManager
from services.llm import LLMService


@dataclass
class BaseChainGuardAgent:
    settings: Settings
    memory: HindsightMemoryManager
    llm_service: LLMService
    name: str
    system_prompt: str

    def narrate(self, task: str, context: dict[str, Any]) -> str:
        return self.llm_service.generate_brief(
            system_prompt=self.system_prompt,
            task=task,
            context=context,
        )
