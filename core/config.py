import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/faratech_news",
)

GAPGPT_API_KEY = os.getenv("GAPGPT_API_KEY", "")
GAPGPT_BASE_URL = os.getenv("GAPGPT_BASE_URL", "https://api.gapgpt.app/v1")
GAPGPT_DEFAULT_MODEL = os.getenv("GAPGPT_DEFAULT_MODEL", "gapgpt-qwen-3.6")
GAPGPT_TRANSLATION_MODEL = os.getenv("GAPGPT_TRANSLATION_MODEL", GAPGPT_DEFAULT_MODEL)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

_cors_raw = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]

# Automatic crawler scheduler (runs every N minutes, 24/7)
CRAWLER_INTERVAL_MINUTES = int(os.getenv("CRAWLER_INTERVAL_MINUTES", "60"))
AUTO_CRAWLER_ENABLED = os.getenv("AUTO_CRAWLER_ENABLED", "true").lower() in (
    "1",
    "true",
    "yes",
    "y",
    "on",
)
