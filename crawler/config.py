import os

CRAWLER_USER_AGENT = os.getenv("CRAWLER_USER_AGENT", "")
CRAWLER_REQUEST_TIMEOUT = float(os.getenv("CRAWLER_REQUEST_TIMEOUT", "60"))
CRAWLER_MAX_RETRIES = int(os.getenv("CRAWLER_MAX_RETRIES", "3"))
CRAWLER_USE_CURL_CFFI = os.getenv("CRAWLER_USE_CURL_CFFI", "true").lower() in (
    "1",
    "true",
    "yes",
)
CRAWLER_IMPERSONATE = os.getenv("CRAWLER_IMPERSONATE", "chrome120")
CRAWLER_DEFAULT_LIMIT = int(os.getenv("CRAWLER_DEFAULT_LIMIT", "10"))
