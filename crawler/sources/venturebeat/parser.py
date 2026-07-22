from typing import Optional
from urllib.parse import urlparse

from crawler.rss import parse_generic_article_page
from crawler.schemas import CrawledArticle
from crawler.sources.venturebeat import config


def normalize_article_url(url: str) -> Optional[str]:
    if not url:
        return None
    parsed = urlparse(url.split("?")[0].split("#")[0])
    if parsed.netloc not in config.ALLOWED_HOSTS:
        return None
    if not parsed.path or parsed.path == "/":
        return None
    path = parsed.path.rstrip("/")
    if not path:
        return None
    # Prefer https + canonical host from BASE_URL
    base = config.BASE_URL.rstrip("/")
    return f"{base}{path}/" if not path.endswith((".html", ".htm")) else f"{base}{path}"


def parse_article_page(
    html: str,
    source_url: str,
    *,
    fallback_title: Optional[str] = None,
) -> CrawledArticle:
    return parse_generic_article_page(
        html,
        source_url,
        fallback_title=fallback_title,
    )
