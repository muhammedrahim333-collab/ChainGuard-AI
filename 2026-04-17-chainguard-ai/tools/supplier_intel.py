from __future__ import annotations

from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class SupplierIntelTool:
    web_search: any

    def scrape_website(self, url: str) -> dict:
        if not url:
            return {"website_summary": "No supplier website available."}
        try:
            response = requests.get(url, timeout=15, headers={"User-Agent": "ChainGuardAI/1.0"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join(soup.get_text(" ", strip=True).split())
            return {"website_summary": text[:500]}
        except Exception as exc:
            return {"website_summary": f"Website scrape unavailable: {exc}"}

    def monitor_supplier(self, supplier, disruption_hint: str = "") -> dict:
        query = f"{supplier.name} {supplier.city} {supplier.product} supplier news disruption India {disruption_hint}".strip()
        search_hits = self.web_search.search(query, max_results=4)
        website = self.scrape_website(supplier.website)
        return {"query": query, "search_hits": search_hits, **website}
