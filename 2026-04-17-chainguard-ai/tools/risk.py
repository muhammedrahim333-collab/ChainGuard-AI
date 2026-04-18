from __future__ import annotations

from dataclasses import dataclass

from models.risk import SupplierRiskAssessment


@dataclass
class RiskScoringTool:
    def score_supplier(self, supplier, signals: dict, disruption_hint: str = "") -> SupplierRiskAssessment:
        score = 10
        reasoning = []

        news_hits = signals.get("supplier_news", {}).get("search_hits", [])
        logistics_hits = signals.get("logistics", {}).get("logistics_hits", [])
        scheme_hits = signals.get("schemes", {}).get("scheme_hits", [])
        weather_hits = signals.get("weather", {}).get("hits", [])
        memory_text = signals.get("memory", "")

        if news_hits:
            score += min(20, len(news_hits) * 4)
            reasoning.append("External news and supplier signals are active.")
        if logistics_hits:
            score += min(18, len(logistics_hits) * 4)
            reasoning.append("Logistics environment shows potential delay indicators.")
        if weather_hits:
            score += 12
            reasoning.append("Weather-related disruption chatter is present.")
        if disruption_hint:
            score += 18
            reasoning.append(f"Simulation or live disruption hint matched: {disruption_hint}.")
        if "No relevant memory found." not in memory_text and memory_text:
            score += 10
            reasoning.append("Historical memory contains related incidents.")
        if scheme_hits:
            score -= 4
            reasoning.append("Government support options may soften the impact.")
        if supplier.lead_time_days > 10:
            score += 8
            reasoning.append("Longer lead time increases operational fragility.")

        score = max(0, min(100, score))
        severity = "healthy" if score < 35 else "watch" if score < 65 else "critical"
        delay_probability = round(min(0.95, 0.15 + score / 120), 2)
        profit_impact = round(max(15000, supplier.quantity * max(supplier.unit_cost_inr, 1) * delay_probability * 0.6), 2)

        if not reasoning:
            reasoning.append("No strong disruption signals found. Supplier remains stable.")

        return SupplierRiskAssessment(
            supplier_id=supplier.supplier_id,
            supplier_name=supplier.name,
            risk_score=score,
            severity_label=severity,
            reasoning=reasoning,
            delay_probability=delay_probability,
            profit_impact_inr=profit_impact,
        )
