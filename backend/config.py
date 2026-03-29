import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    MAX_CSV_SIZE_MB: int = int(os.getenv("MAX_CSV_SIZE_MB", "5"))
    MAX_PASTE_CHARS: int = int(os.getenv("MAX_PASTE_CHARS", "50000"))
    MAX_DAX_ROWS: int = int(os.getenv("MAX_DAX_ROWS", "1000"))
    # Phase 2
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET", "")
    REDIRECT_URI: str = os.getenv("REDIRECT_URI", "http://localhost:8000/api/auth/callback")
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "change-me")


settings = Settings()
