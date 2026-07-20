from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from crawler.metadata import (
    extract_category_from_meta,
    extract_cover_image_url,
    extract_tags_from_soup,
)
from crawler.schemas import CrawledArticle
from crawler.sources.hubspot import config


def _normalize_article_url(href: str) -> Optional[str]:
    if not href or href.startswith("#"):
        return None

    absolute = urljoin(config.BASE_URL, href.split("?")[0].rstrip("/"))
    parsed = urlparse(absolute)
    if parsed.netloc not in config.ALLOWED_HOSTS:
        return None

    path = parsed.path.strip("/")
    if not path:
        return None

    parts = path.split("/")
    if len(parts) < 2:
        return None
    if parts[0] not in config.ALLOWED_SECTIONS:
        return None
    if parts[1] in {"topic", "author", "tag"}:
        return None

    return f"{config.BASE_URL}/{'/'.join(parts)}"


def extract_article_urls(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    urls: list[str] = []

    for anchor in soup.find_all("a", href=True):
        url = _normalize_article_url(anchor["href"])
        if url and url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def _meta_content(soup: BeautifulSoup, *, property_name: str) -> Optional[str]:
    tag = soup.find("meta", attrs={"property": property_name})
    if isinstance(tag, Tag) and tag.get("content"):
        return str(tag["content"]).strip()
    return None


def _first_text(soup: BeautifulSoup, selector: str) -> Optional[str]:
    node = soup.select_one(selector)
    if node is None:
        return None
    text = node.get_text(separator=" ", strip=True)
    return text or None


def _category_from_source_url(source_url: str) -> Optional[str]:
    path = urlparse(source_url).path.strip("/")
    if not path:
        return None
    section = path.split("/")[0]
    if section in config.ALLOWED_SECTIONS:
        return section.title()
    return None


def parse_article_page(html: str, source_url: str) -> CrawledArticle:
    soup = BeautifulSoup(html, "html.parser")

    title = _first_text(soup, "h1") or _meta_content(soup, property_name="og:title")
    if not title:
        raise ValueError(f"Could not extract title from {source_url}")

    content_node = soup.select_one(".blog-post-body")
    if content_node is None:
        content_node = soup.select_one("main")
    if content_node is None:
        raise ValueError(f"Could not extract article body from {source_url}")

    content = content_node.get_text(separator="\n\n", strip=True)
    if not content:
        raise ValueError(f"Article body is empty at {source_url}")

    summary = _meta_content(soup, property_name="og:description")
    author = _first_text(soup, '[rel="author"]') or _first_text(soup, ".author-name")
    category = _category_from_source_url(source_url) or extract_category_from_meta(soup)
    tags = extract_tags_from_soup(soup)
    cover_image_url = extract_cover_image_url(soup, base_url=source_url)

    return CrawledArticle(
        title=title,
        content=content,
        summary=summary,
        category=category,
        tags=tags or None,
        cover_image_url=cover_image_url,
        source_url=source_url,
        author=author,
    )
