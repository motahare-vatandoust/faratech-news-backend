import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/faratech_news",
)

GAPGPT_API_KEY = os.getenv("GAPGPT_API_KEY", "")
GAPGPT_BASE_URL = os.getenv("GAPGPT_BASE_URL", "https://api.gapgpt.app/v1")
GAPGPT_DEFAULT_MODEL = os.getenv("GAPGPT_DEFAULT_MODEL", "gpt-4o")
