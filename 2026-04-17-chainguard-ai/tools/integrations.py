from __future__ import annotations

import json
import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText
from pathlib import Path

import requests


@dataclass
class WhatsAppAlertTool:
    settings: any

    def send(self, message: str) -> dict:
        if not (
            self.settings.whatsapp_access_token
            and self.settings.whatsapp_phone_number_id
            and self.settings.whatsapp_recipient_phone
        ):
            return {"status": "skipped", "reason": "WhatsApp credentials missing"}
        try:
            response = requests.post(
                f"https://graph.facebook.com/v22.0/{self.settings.whatsapp_phone_number_id}/messages",
                headers={
                    "Authorization": f"Bearer {self.settings.whatsapp_access_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "messaging_product": "whatsapp",
                    "to": self.settings.whatsapp_recipient_phone,
                    "type": "text",
                    "text": {"body": message[:4096]},
                },
                timeout=20,
            )
            response.raise_for_status()
            return {"status": "sent", "provider": "whatsapp"}
        except Exception as exc:
            return {"status": "failed", "reason": str(exc)}


@dataclass
class EmailAlertTool:
    settings: any

    def send(self, subject: str, body: str) -> dict:
        if not (self.settings.smtp_host and self.settings.smtp_username and self.settings.alert_email_to):
            return {"status": "skipped", "reason": "SMTP configuration missing"}
        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = self.settings.smtp_username
            msg["To"] = self.settings.alert_email_to

            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as server:
                server.starttls()
                server.login(self.settings.smtp_username, self.settings.smtp_password)
                server.sendmail(self.settings.smtp_username, [self.settings.alert_email_to], msg.as_string())
            return {"status": "sent", "provider": "email"}
        except Exception as exc:
            return {"status": "failed", "reason": str(exc)}


@dataclass
class GoogleSheetsTool:
    settings: any

    def append_rows(self, rows: list[dict]) -> dict:
        if not (self.settings.google_service_account_json and self.settings.google_sheets_id):
            return {"status": "skipped", "reason": "Google Sheets configuration missing"}
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            raw_creds = self.settings.google_service_account_json
            if Path(raw_creds).exists():
                creds_info = json.loads(Path(raw_creds).read_text(encoding="utf-8"))
            else:
                creds_info = json.loads(raw_creds)
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(self.settings.google_sheets_id).sheet1
            for row in rows:
                sheet.append_row(list(row.values()))
            return {"status": "updated", "rows": len(rows)}
        except Exception as exc:
            return {"status": "failed", "reason": str(exc)}


@dataclass
class ReportTool:
    def build_alert_text(self, supplier, assessment, mitigation) -> str:
        action = mitigation["actions"][0]
        return (
            f"ChainGuard AI alert: {supplier.name} in {supplier.city} is at {assessment.severity_label.upper()} risk "
            f"({assessment.risk_score}/100). Delay probability {assessment.delay_probability:.0%}. "
            f"Potential impact around Rs. {assessment.profit_impact_inr:,.0f}. Next step: {action}"
        )

    def build_report(self, supplier, assessment, mitigation, run_id: str) -> str:
        lines = [
            f"Run ID: {run_id}",
            f"Supplier: {supplier.name}",
            f"City: {supplier.city}, {supplier.state}",
            f"Product: {supplier.product}",
            f"Risk Score: {assessment.risk_score}/100 ({assessment.severity_label})",
            f"Delay Probability: {assessment.delay_probability:.0%}",
            f"Potential Profit Impact: Rs. {assessment.profit_impact_inr:,.0f}",
            "Reasoning:",
        ]
        lines.extend(f"- {item}" for item in assessment.reasoning[:5])
        lines.append("Mitigations:")
        lines.extend(f"- {item}" for item in mitigation["actions"])
        lines.append(f"Memory Insight: {mitigation['memory_hint']}")
        return "\n".join(lines)
