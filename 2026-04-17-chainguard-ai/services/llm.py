from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from config import Settings

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None


@dataclass
class LLMService:
    settings: Settings

    def chat_model(self):
        if not self.settings.groq_api_key or ChatGroq is None:
            return None
        try:
            return ChatGroq(
                api_key=self.settings.groq_api_key,
                model=self.settings.groq_model,
                temperature=0.2,
            )
        except Exception:
            return None

    def generate_brief(self, system_prompt: str, task: str, context: dict[str, Any]) -> str:
        model = self.chat_model()
        if model is None:
            impact = context.get("profit_saved_inr", 0)
            hint = context.get("disruption_hint", "")
            return (
                f"ChainGuard AI completed the cycle. Risk hot spots were reviewed for the tracked suppliers. "
                f"Disruption focus: {hint or 'routine monitoring'}. Estimated profit protected: Rs. {impact:,.0f}."
            )
        prompt = (
            f"{system_prompt}\n\n"
            f"Task: {task}\n"
            f"Return a short owner-facing operational summary in natural English with light Hindi/Punjabi flavor.\n"
            f"Context JSON:\n{json.dumps(self._safe_context(context), default=str)[:7000]}"
        )
        try:
            response = model.invoke(prompt)
            return getattr(response, "content", str(response))
        except Exception:
            return "ChainGuard AI completed the monitoring cycle and prepared next actions."

    def answer_question(
        self,
        question: str,
        context: dict[str, Any],
        recalled_memory: str = "",
        recent_messages: list[dict[str, str]] | None = None,
    ) -> str:
        model = self.chat_model()
        suppliers = context.get("suppliers", [])
        heuristic_answer = self._heuristic_answer(question, context, recalled_memory, recent_messages or [])
        if model is None:
            return heuristic_answer

        prompt = (
            "You are ChainGuard AI's operator assistant for Indian SMEs.\n"
            "Answer the user's supply-chain question using the available supplier context, the last autonomous run, and recalled Hindsight memory.\n"
            "Be concise, practical, and natural. Prefer English with light Hindi/Punjabi flavor when useful.\n"
            "If risk data is missing, say so clearly and suggest running the autonomous cycle.\n\n"
            f"User question: {question}\n"
            f"Recalled memory: {recalled_memory or 'No relevant memory found.'}\n"
            f"Recent chat messages: {json.dumps((recent_messages or [])[-4:], default=str)}\n"
            f"Context JSON:\n{json.dumps(self._safe_context(context), default=str)[:7000]}"
        )
        try:
            response = model.invoke(prompt)
            content = getattr(response, "content", str(response))
            return content or heuristic_answer
        except Exception:
            return heuristic_answer

    def _supplier_name(self, item: Any) -> str:
        if isinstance(item, dict):
            return str(item.get("name", item))
        return str(getattr(item, "name", item))

    def _heuristic_answer(
        self,
        question: str,
        context: dict[str, Any],
        recalled_memory: str,
        recent_messages: list[dict[str, str]],
    ) -> str:
        question_l = question.lower()
        suppliers = context.get("suppliers", [])
        assessments = context.get("risk_assessments", {}) or {}
        last_assistant_message = ""
        for message in reversed(recent_messages):
            if message.get("role") == "assistant":
                last_assistant_message = message.get("content", "")
                break

        if "hindi" in question_l or "translate" in question_l:
            if last_assistant_message:
                return (
                    "Simple Hindi mein: "
                    "Iska matlab hai ki system keh raha hai ki abhi live risk scoring data ya to run nahi hua hai "
                    "ya current question ke liye enough fresh result nahi mila. Pehle autonomous cycle chalao, "
                    "phir system zyada exact batayega ki kaunsa supplier risky hai, kitna nuksan ho sakta hai, "
                    "aur kya action lena chahiye."
                )
            return (
                "Simple Hindi mein: abhi mere paas previous answer ka context nahi hai. "
                "Pehle autonomous cycle chalao ya ek specific question pucho, phir main use simple Hindi mein samjha dunga."
            )

        if "ludhiana" in question_l and (
            "blocked" in question_l
            or "block" in question_l
            or "strike" in question_l
            or "road" in question_l
            or "transport" in question_l
        ):
            impacted = [
                self._supplier_name(item)
                for item in suppliers
                if str(getattr(item, "city", "")).lower() == "ludhiana"
            ]
            impacted_text = ", ".join(impacted) if impacted else "your Ludhiana-linked suppliers"
            if assessments:
                high_risk = [
                    item for item in assessments.values()
                    if item.supplier_name in impacted and item.risk_score >= 35
                ]
                top_note = ""
                if high_risk:
                    top_item = sorted(high_risk, key=lambda item: item.risk_score, reverse=True)[0]
                    top_note = (
                        f" Right now, {top_item.supplier_name} is the most exposed at "
                        f"{top_item.risk_score}/100."
                    )
                return (
                    f"If Ludhiana is blocked, act fast on {impacted_text}.{top_note} "
                    f"First, confirm dispatch status and ETA within the next few hours. "
                    f"Second, activate backup sourcing outside Ludhiana for yarn or textile inputs. "
                    f"Third, protect 5 to 7 days of buffer stock for critical orders. "
                    f"Fourth, shift shipments through alternate routing via nearby hubs if possible. "
                    f"Fifth, inform customers and internal production teams early so margin damage stays controlled."
                )
            return (
                f"If Ludhiana is blocked, the first likely impact is on {impacted_text}. "
                f"My practical suggestion is: confirm pending dispatches immediately, line up one backup supplier "
                f"outside Ludhiana, hold temporary safety stock for urgent orders, and re-plan transport routes today. "
                f"For a proper risk-ranked answer, run the autonomous cycle with `Strike in Ludhiana` selected."
            )

        if assessments:
            ranked = sorted(
                assessments.values(),
                key=lambda item: getattr(item, "risk_score", 0),
                reverse=True,
            )
            top = ranked[0]
            if "why" in question_l or "reason" in question_l:
                matched = None
                for item in ranked:
                    supplier_name_l = item.supplier_name.lower()
                    if any(token in supplier_name_l for token in question_l.split()):
                        matched = item
                        break
                target = matched or top
                return (
                    f"{target.supplier_name} is highly impacted because its current risk score is "
                    f"{target.risk_score}/100 with delay probability {target.delay_probability:.0%}. "
                    f"Key reasons are: {'; '.join(target.reasoning[:3])}. "
                    f"Estimated exposure is around Rs. {target.profit_impact_inr:,.0f}."
                )
            if "riskiest" in question_l or "highest risk" in question_l or "most risky" in question_l:
                return (
                    f"The riskiest supplier right now is {top.supplier_name} at {top.risk_score}/100 "
                    f"({top.severity_label}). Delay probability is {top.delay_probability:.0%} and the estimated "
                    f"profit impact is Rs. {top.profit_impact_inr:,.0f}. "
                    f"Main reasons: {'; '.join(top.reasoning[:2])}."
                )
            if "profit" in question_l or "impact" in question_l or "loss" in question_l:
                total = sum(getattr(item, "profit_impact_inr", 0) for item in ranked)
                return (
                    f"Current projected gross disruption impact across tracked suppliers is about Rs. {total:,.0f}. "
                    f"The biggest single exposure is {top.supplier_name} at around Rs. {top.profit_impact_inr:,.0f}."
                )
            if "supplier" in question_l or "risk" in question_l:
                top_three = ", ".join(
                    f"{item.supplier_name} ({item.risk_score}/100)"
                    for item in ranked[:3]
                )
                return f"Top current risk suppliers are: {top_three}."

        if suppliers:
            ranked_suppliers = sorted(
                suppliers,
                key=lambda item: (
                    getattr(item, "lead_time_days", 0),
                    getattr(item, "unit_cost_inr", 0),
                    getattr(item, "quantity", 0),
                ),
                reverse=True,
            )
            top_supplier = ranked_suppliers[0]
            if "riskiest" in question_l or "highest risk" in question_l or "most risky" in question_l:
                memory_note = (
                    f"Memory hint: {recalled_memory}"
                    if recalled_memory and recalled_memory != "No relevant memory found."
                    else "No strong historical memory match yet."
                )
                return (
                    f"I have not run the autonomous scoring cycle yet, so I do not have a live risk score. "
                    f"As a quick preview, {self._supplier_name(top_supplier)} looks most fragile operationally because it has "
                    f"a lead time of {getattr(top_supplier, 'lead_time_days', 0)} days with unit cost around "
                    f"Rs. {getattr(top_supplier, 'unit_cost_inr', 0):,.0f}. {memory_note} "
                    f"Run the autonomous cycle for a proper risk ranking."
                )

        supplier_names = ", ".join(self._supplier_name(item) for item in suppliers[:4]) if suppliers else "no suppliers loaded"
        memory_note = recalled_memory if recalled_memory and recalled_memory != "No relevant memory found." else "No strong historical memory match."
        return (
            f"Tracked suppliers include {supplier_names}. Historical context: {memory_note}. "
            f"For a precise operational answer, run the autonomous cycle and then ask again."
        )

    def _safe_context(self, context: dict[str, Any]) -> dict[str, Any]:
        safe = dict(context)
        if "suppliers" in safe:
            safe["suppliers"] = [getattr(item, "model_dump", lambda: str(item))() for item in safe["suppliers"]]
        if "risk_assessments" in safe:
            safe["risk_assessments"] = {
                key: getattr(value, "model_dump", lambda: str(value))()
                for key, value in safe["risk_assessments"].items()
            }
        if "actions" in safe:
            safe["actions"] = {
                key: {
                    "alert_text": value.get("alert_text", ""),
                    "whatsapp": value.get("whatsapp", {}),
                    "email": value.get("email", {}),
                    "sheets": value.get("sheets", {}),
                }
                for key, value in safe["actions"].items()
            }
        return safe
