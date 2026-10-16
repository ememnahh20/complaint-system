"""Lahat ng settings ay galing sa environment variables (.env)."""
import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # optional lang ang python-dotenv
    pass


@dataclass(frozen=True)
class Config:
    secret_key: str
    admin_password: str
    sheet_id: str
    worksheet_name: str
    credentials_file: str
    gmail_user: str
    gmail_app_password: str
    dev_mode: bool

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            secret_key=os.getenv("SECRET_KEY", "dev-secret-change-me"),
            admin_password=os.getenv("ADMIN_PASSWORD", "admin123"),
            sheet_id=os.getenv("GOOGLE_SHEET_ID", ""),
            worksheet_name=os.getenv("GOOGLE_WORKSHEET", "Complaints"),
            credentials_file=os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
            gmail_user=os.getenv("GMAIL_USER", ""),
            gmail_app_password=os.getenv("GMAIL_APP_PASSWORD", ""),
            dev_mode=os.getenv("DEV_MODE", "false").lower() == "true",
        )
