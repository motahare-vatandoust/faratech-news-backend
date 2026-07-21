from typing import Optional
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup, Tag

from crawler.metadata import (
    extract_category_from_meta,
    extract_cover_image_url,
    extract_tags_from_soup,
)
from crawler.schemas import CrawledArticle
from crawler.sources.nngroup import config


def _normalize_article_url(url: str) -> Optional[str]:
    if not url:
        return None

    parsed = urlparse(url.split("?")[0])
    if parsed.netloc not in config.ALLOWED_HOSTS:
        return None
    if not parsed.path.startswith(config.ARTICLE_PATH_PREFIX):
        return None

    clean_path = parsed.path.rstrip("/")
    if clean_path == config.ARTICLE_PATH_PREFIX.rstrip("/"):
        return None

    slug = clean_path[len(config.ARTICLE_PATH_PREFIX.rstrip("/")) :].lstrip("/")
    if not slug or "/" in slug:
        return None

    return f"{config.BASE_URL}{config.ARTICLE_PATH_PREFIX}{slug}/"


def extract_article_urls_from_feed(feed_xml: str) -> list[str]:
    try:
        root = ET.fromstring(feed_xml.lstrip())
    except ET.ParseError:
        return []

    seen: set[str] = set()
    urls: list[str] = []

    for item in root.findall(".//item"):
        raw_url = (item.findtext("link") or "").strip()
        url = _normalize_article_url(raw_url)
        if url and url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def extract_title_map_from_feed(feed_xml: str) -> dict[str, str]:
    try:
        root = ET.fromstring(feed_xml.lstrip())
    except ET.ParseError:
        return {}

    mapping: dict[str, str] = {}
    for item in root.findall(".//item"):
        raw_url = (item.findtext("link") or "").strip()
        title = (item.findtext("title") or "").strip()
        url = _normalize_article_url(raw_url)
        if url and title:
            mapping[url.rstrip("/")] = title
    return mapping


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


def parse_article_page(
    html: str,
    source_url: str,
    *,
    fallback_title: Optional[str] = None,
) -> CrawledArticle:
    soup = BeautifulSoup(html, "html.parser")

    title = (
        _first_text(soup, "h1")
        or _meta_content(soup, property_name="og:title")
        or fallback_title
    )
    if not title:
        raise ValueError(f"Could not extract title from {source_url}")

    content_node = (
        soup.select_one(".article-content")
        or soup.select_one("article")
        or soup.select_one("main")
    )
    if content_node is None:
        raise ValueError(f"Could not extract article body from {source_url}")

    content = content_node.get_text(separator="\n\n", strip=True)
    if not content:
        raise ValueError(f"Article body is empty at {source_url}")

    summary = _meta_content(soup, property_name="og:description")
    author = _first_text(soup, ".article-meta-author") or _first_text(
        soup, "a[rel='author']"
    )
    category = extract_category_from_meta(soup) or "UX"
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
