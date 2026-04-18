from __future__ import annotations

from typing import Any, TypedDict


class ChainGuardState(TypedDict, total=False):
    run_id: str
    suppliers: list[Any]
    disruption_hint: str
    language: str
    monitor_output: dict[str, Any]
    risk_assessments: dict[str, Any]
    mitigations: dict[str, Any]
    actions: dict[str, Any]
    summary: str
    profit_saved_inr: float
    logs: list[str]
