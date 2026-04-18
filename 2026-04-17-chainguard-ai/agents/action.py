from __future__ import annotations

from dataclasses import dataclass

from agents.base import BaseChainGuardAgent
from agents.prompts import ACTION_PROMPT
from tools.integrations import EmailAlertTool, GoogleSheetsTool, ReportTool, WhatsAppAlertTool


@dataclass
class ActionAgent(BaseChainGuardAgent):
    whatsapp: WhatsAppAlertTool
    email: EmailAlertTool
    sheets: GoogleSheetsTool
    reports: ReportTool

    @classmethod
    def create(cls, settings, memory, llm_service):
        return cls(
            settings=settings,
            memory=memory,
            llm_service=llm_service,
            name="Action Agent",
            system_prompt=ACTION_PROMPT,
            whatsapp=WhatsAppAlertTool(settings),
            email=EmailAlertTool(settings),
            sheets=GoogleSheetsTool(settings),
            reports=ReportTool(),
        )

    def run(self, suppliers, assessments, mitigations, run_id: str) -> dict:
        actions = {}
        rows = []
        for supplier in suppliers:
            assessment = assessments[supplier.supplier_id]
            mitigation = mitigations[supplier.supplier_id]
            alert_text = self.reports.build_alert_text(supplier, assessment, mitigation)
            report_blob = self.reports.build_report(supplier, assessment, mitigation, run_id)

            whatsapp_result = self.whatsapp.send(alert_text)
            email_result = self.email.send(
                subject=f"[ChainGuard AI] {supplier.name} risk update",
                body=report_blob,
            )
            rows.append(
                {
                    "run_id": run_id,
                    "supplier": supplier.name,
                    "city": supplier.city,
                    "product": supplier.product,
                    "risk_score": assessment.risk_score,
                    "severity": assessment.severity_label,
                    "profit_impact_inr": assessment.profit_impact_inr,
                }
            )
            actions[supplier.supplier_id] = {
                "alert_text": alert_text,
                "report": report_blob,
                "whatsapp": whatsapp_result,
                "email": email_result,
            }

        sheet_result = self.sheets.append_rows(rows)
        for payload in actions.values():
            payload["sheets"] = sheet_result
        return actions
