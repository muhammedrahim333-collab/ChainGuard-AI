from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass
class WebSearchTool:
    settings: any

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        if self.settings.tavily_api_key:
            return self._tavily(query, max_results)
        if self.settings.serper_api_key:
            return self._serper(query, max_results)
        return [{"title": "Demo mode", "snippet": f"No search key configured. Query prepared: {query}", "url": ""}]

    def _tavily(self, query: str, max_results: int) -> list[dict]:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": self.settings.tavily_api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("results", [])

    def _serper(self, query: str, max_results: int) -> list[dict]:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": self.settings.serper_api_key},
            json={"q": query, "num": max_results},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("organic", [])
