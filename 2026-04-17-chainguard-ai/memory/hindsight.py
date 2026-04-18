from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config import Settings

try:
    from hindsight_client import Hindsight
except Exception:
    Hindsight = None

try:
    from hindsight_langgraph import configure as configure_hindsight
    from hindsight_langgraph import create_hindsight_tools
except Exception:
    configure_hindsight = None
    create_hindsight_tools = None

try:
    from langchain_core.tools import StructuredTool
except Exception:
    StructuredTool = None


@dataclass
class HindsightMemoryManager:
    settings: Settings

    def __post_init__(self):
        self._client = None
        self._configure_hindsight()
        self._ensure_local_store()

    def _configure_hindsight(self) -> None:
        if configure_hindsight and self.settings.hindsight_api_url:
            try:
                configure_hindsight(
                    hindsight_api_url=self.settings.hindsight_api_url,
                    api_key=self.settings.hindsight_api_key or None,
                    budget="mid",
                    tags=["source:langgraph", "app:chainguard-ai"],
                )
            except Exception:
                pass

    def _ensure_local_store(self) -> None:
        path = self.settings.local_memory_path
        if not path.exists():
            path.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")

    @property
    def bank_id(self) -> str:
        return self.settings.hindsight_bank_id

    def client(self):
        if self._client is not None:
            return self._client
        if Hindsight is None:
            return None
        try:
            self._client = Hindsight(
                base_url=self.settings.hindsight_api_url,
                api_key=self.settings.hindsight_api_key or None,
                timeout=30.0,
            )
            try:
                self._client.create_bank(bank_id=self.bank_id, name="ChainGuard AI")
            except Exception:
                pass
        except Exception:
            self._client = None
        return self._client

    def build_tools(self) -> list[Any]:
        client = self.client()
        if client and create_hindsight_tools:
            try:
                return create_hindsight_tools(client=client, bank_id=self.bank_id)
            except Exception:
                pass
        if StructuredTool is None:
            return []
        return [
            StructuredTool.from_function(
                name="retain_memory",
                func=lambda content: self.retain(content),
                description="Store supply chain facts and outcomes in Hindsight memory.",
            ),
            StructuredTool.from_function(
                name="recall_memory",
                func=lambda query: self.recall(query),
                description="Recall relevant supply chain memories from Hindsight.",
            ),
            StructuredTool.from_function(
                name="reflect_on_memory",
                func=lambda query: self.reflect(query),
                description="Reflect on remembered supplier patterns and incident outcomes.",
            ),
        ]

    def retain(self, content: str, context: str | None = None, tags: list[str] | None = None) -> str:
        client = self.client()
        if client:
            try:
                client.retain(
                    bank_id=self.bank_id,
                    content=content,
                    context=context,
                    tags=tags,
                )
                return "stored_in_hindsight"
            except Exception:
                pass
        self._append_local({"type": "retain", "content": content, "context": context, "tags": tags or []})
        return "stored_locally"

    def recall(self, query: str) -> str:
        client = self.client()
        if client:
            try:
                result = client.recall(bank_id=self.bank_id, query=query)
                items = []
                for row in getattr(result, "results", [])[:5]:
                    text = getattr(row, "text", "") or getattr(row, "content", "")
                    if text:
                        items.append(text)
                return "\n".join(items) if items else "No relevant memory found."
            except Exception:
                pass
        data = self._read_local()
        matches = [item["content"] for item in data["items"] if query.lower() in item.get("content", "").lower()]
        return "\n".join(matches[:5]) if matches else "No relevant memory found."

    def reflect(self, query: str) -> str:
        client = self.client()
        if client:
            try:
                result = client.reflect(bank_id=self.bank_id, query=query)
                answer = getattr(result, "answer", None) or getattr(result, "content", None) or str(result)
                return answer
            except Exception:
                pass
        recalled = self.recall(query)
        return f"Reflection fallback: {recalled}"

    def _append_local(self, payload: dict[str, Any]) -> None:
        data = self._read_local()
        data["items"].append(payload)
        Path(self.settings.local_memory_path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _read_local(self) -> dict[str, Any]:
        path = Path(self.settings.local_memory_path)
        return json.loads(path.read_text(encoding="utf-8"))
