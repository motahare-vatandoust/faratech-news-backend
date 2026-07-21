from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from crawler.metadata import (
    extract_category_from_meta,
    extract_cover_image_url,
    extract_tags_from_soup,
)
from crawler.schemas import CrawledArticle
from crawler.sources.itsnicethat import config


def _normalize_article_url(href: str) -> Optional[str]:
    if not href or href.startswith("#"):
        return None

    absolute = urljoin(config.BASE_URL, href.split("?")[0].rstrip("/"))
    parsed = urlparse(absolute)

    if parsed.netloc not in config.ALLOWED_HOSTS:
        return None

    path = parsed.path if parsed.path.endswith("/") else f"{parsed.path}/"
    matched_prefix = None
    for prefix in config.ARTICLE_PATH_PREFIXES:
        if path.startswith(prefix):
            matched_prefix = prefix
            break
    if matched_prefix is None:
        return None

    slug = path[len(matched_prefix) :].strip("/")
    if not slug or "/" in slug:
        return None

    return f"{config.BASE_URL}{matched_prefix}{slug}"


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


def _extract_content(soup: BeautifulSoup) -> Optional[str]:
    for selector in ("article", "main"):
        node = soup.select_one(selector)
        if node is None:
            continue
        text = node.get_text(separator="\n\n", strip=True)
        if text:
            return text
    return None


def parse_article_page(html: str, source_url: str) -> CrawledArticle:
    soup = BeautifulSoup(html, "html.parser")

    title = (
        _first_text(soup, "h1")
        or _meta_content(soup, property_name="og:title")
    )
    if not title:
        raise ValueError(f"Could not extract title from {source_url}")

    content = _extract_content(soup)
    if not content:
        raise ValueError(f"Could not extract article body from {source_url}")

    summary = _meta_content(soup, property_name="og:description")
    category = extract_category_from_meta(soup)
    tags = extract_tags_from_soup(soup)
    cover_image_url = extract_cover_image_url(soup, base_url=source_url)
    author = _first_text(soup, "a[rel='author']")

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
