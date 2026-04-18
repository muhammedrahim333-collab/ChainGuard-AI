from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(slots=True)
class Settings:
    app_name: str = "ChainGuard AI"
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    hindsight_api_url: str = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")
    hindsight_api_key: str = os.getenv("HINDSIGHT_API_KEY", "")
    hindsight_bank_id: str = os.getenv("HINDSIGHT_BANK_ID", "chainguard-ai")

    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")

    whatsapp_access_token: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    whatsapp_phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    whatsapp_recipient_phone: str = os.getenv("WHATSAPP_RECIPIENT_PHONE", "")

    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    alert_email_to: str = os.getenv("ALERT_EMAIL_TO", "")

    google_service_account_json: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    google_sheets_id: str = os.getenv("GOOGLE_SHEETS_ID", "")

    local_memory_path: Path = field(default_factory=lambda: BASE_DIR / "local_memory.json")


settings = Settings()
