import os

CRAWLER_USER_AGENT = os.getenv(
    "CRAWLER_USER_AGENT",
    "FaratechNewsBot/1.0 (+https://github.com/faratech/news-backend)",
)
CRAWLER_REQUEST_TIMEOUT = float(os.getenv("CRAWLER_REQUEST_TIMEOUT", "30"))
CRAWLER_DEFAULT_LIMIT = int(os.getenv("CRAWLER_DEFAULT_LIMIT", "10"))
