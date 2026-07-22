from typing import Optional
from urllib.parse import urlparse

from crawler.rss import parse_generic_article_page
from crawler.schemas import CrawledArticle
from crawler.sources.thenewstack import config


def normalize_article_url(url: str) -> Optional[str]:
    if not url:
        return None
    parsed = urlparse(url.split("?")[0].split("#")[0])
    if parsed.netloc not in config.ALLOWED_HOSTS:
        return None
    path = parsed.path.rstrip("/")
    if not path or path == "/":
        return None
    return f"{config.BASE_URL}{path}/"


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
        content_selectors=(
            ".content-column-post-body",
            ".content",
            "article",
            "main",
        ),
    )
