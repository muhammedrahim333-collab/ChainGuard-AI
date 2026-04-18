from __future__ import annotations

from dataclasses import dataclass

from agents.base import BaseChainGuardAgent
from agents.prompts import MONITOR_PROMPT
from tools.external_data import IndiaIntelTool
from tools.search import WebSearchTool
from tools.supplier_intel import SupplierIntelTool


@dataclass
class MonitorAgent(BaseChainGuardAgent):
    web_search: WebSearchTool
    supplier_intel: SupplierIntelTool
    india_intel: IndiaIntelTool

    @classmethod
    def create(cls, settings, memory, llm_service):
        web_search = WebSearchTool(settings)
        return cls(
            settings=settings,
            memory=memory,
            llm_service=llm_service,
            name="Monitor Agent",
            system_prompt=MONITOR_PROMPT,
            web_search=web_search,
            supplier_intel=SupplierIntelTool(web_search),
            india_intel=IndiaIntelTool(settings, web_search),
        )

    def run(self, suppliers, disruption_hint: str = "") -> dict:
        intel = {}
        for supplier in suppliers:
            supplier_news = self.supplier_intel.monitor_supplier(supplier, disruption_hint=disruption_hint)
            weather = self.india_intel.weather_and_event_snapshot(supplier.city)
            market = self.india_intel.agmarknet_snapshot(supplier.product)
            schemes = self.india_intel.government_scheme_alerts(supplier.industry)
            logistics = self.india_intel.logistics_snapshot(supplier.city)
            recall = self.memory.recall(
                f"Past disruptions or warnings for supplier {supplier.name} in {supplier.city} for {supplier.product}"
            )

            intel[supplier.supplier_id] = {
                "supplier_news": supplier_news,
                "weather": weather,
                "market": market,
                "schemes": schemes,
                "logistics": logistics,
                "memory": recall,
            }
        return intel
