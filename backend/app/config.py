import os
from functools import lru_cache


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./proximeet.db")
        self.entra_tenant_id = os.getenv("ENTRA_TENANT_ID", "common")
        self.entra_client_id = os.getenv("ENTRA_CLIENT_ID", "")
        self.entra_audience = os.getenv("ENTRA_AUDIENCE", self.entra_client_id)
        self.entra_issuer = os.getenv(
            "ENTRA_ISSUER",
            f"https://login.microsoftonline.com/{self.entra_tenant_id}/v2.0",
        )
        self.google_places_api_key = os.getenv("GOOGLE_PLACES_API_KEY", "")
        self.presence_default_hours = int(os.getenv("PRESENCE_DEFAULT_HOURS", "6"))
        self.bubble_radius_km = float(os.getenv("BUBBLE_RADIUS_KM", "0.3"))
        self.allow_anonymous = os.getenv("ALLOW_ANONYMOUS", "false").lower() == "true"
        
        # Email configuration
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        
        # Frontend URL for email links
        self.frontend_url = os.getenv("FRONTEND_URL", "https://proximeet.hrconseil.net")


@lru_cache
def get_settings() -> Settings:
    return Settings()
