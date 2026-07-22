"""Shared helpers for RSS/Atom feed-based crawlers."""

from __future__ import annotations

from typing import Callable, Optional
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup, Tag

from crawler.metadata import (
    extract_category_from_meta,
    extract_cover_image_url,
    extract_tags_from_soup,
)
from crawler.schemas import CrawledArticle

NormalizeUrl = Callable[[str], Optional[str]]


def extract_article_urls_from_feed(
    feed_xml: str,
    *,
    normalize_url: NormalizeUrl,
) -> list[str]:
    try:
        root = ET.fromstring(feed_xml.lstrip())
    except ET.ParseError:
        return []

    seen: set[str] = set()
    urls: list[str] = []

    for item in root.findall(".//item"):
        raw_url = (item.findtext("link") or "").strip()
        url = normalize_url(raw_url)
        if url and url not in seen:
            seen.add(url)
            urls.append(url)

    # Atom feeds
    atom_ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//atom:entry", atom_ns):
        link = entry.find("atom:link", atom_ns)
        raw_url = ""
        if link is not None:
            raw_url = (link.get("href") or "").strip()
        url = normalize_url(raw_url)
        if url and url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def extract_title_map_from_feed(
    feed_xml: str,
    *,
    normalize_url: NormalizeUrl,
) -> dict[str, str]:
    try:
        root = ET.fromstring(feed_xml.lstrip())
    except ET.ParseError:
        return {}

    mapping: dict[str, str] = {}
    for item in root.findall(".//item"):
        raw_url = (item.findtext("link") or "").strip()
        title = (item.findtext("title") or "").strip()
        url = normalize_url(raw_url)
        if url and title:
            mapping[url.rstrip("/")] = title

    atom_ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//atom:entry", atom_ns):
        link = entry.find("atom:link", atom_ns)
        raw_url = ""
        if link is not None:
            raw_url = (link.get("href") or "").strip()
        title_node = entry.find("atom:title", atom_ns)
        title = (title_node.text or "").strip() if title_node is not None else ""
        url = normalize_url(raw_url)
        if url and title:
            mapping[url.rstrip("/")] = title

    return mapping


def host_in_allowed(url: str, allowed_hosts: frozenset[str]) -> bool:
    parsed = urlparse(url.split("?")[0])
    return parsed.netloc in allowed_hosts


def meta_content(soup: BeautifulSoup, *, property_name: str) -> Optional[str]:
    tag = soup.find("meta", attrs={"property": property_name})
    if isinstance(tag, Tag) and tag.get("content"):
        return str(tag["content"]).strip()
    name_tag = soup.find("meta", attrs={"name": property_name})
    if isinstance(name_tag, Tag) and name_tag.get("content"):
        return str(name_tag["content"]).strip()
    return None


def first_text(soup: BeautifulSoup, selector: str) -> Optional[str]:
    node = soup.select_one(selector)
    if node is None:
        return None
    text = node.get_text(separator=" ", strip=True)
    return text or None


def parse_generic_article_page(
    html: str,
    source_url: str,
    *,
    fallback_title: Optional[str] = None,
    content_selectors: tuple[str, ...] = (
        "article .entry-content",
        "article .post-content",
        "article .article-content",
        ".entry-content",
        ".post-content",
        ".article-content",
        "article",
        "main",
    ),
) -> CrawledArticle:
    soup = BeautifulSoup(html, "html.parser")

    title = (
        first_text(soup, "h1")
        or meta_content(soup, property_name="og:title")
        or fallback_title
    )
    if not title:
        raise ValueError(f"Could not extract title from {source_url}")

    content_node = None
    for selector in content_selectors:
        content_node = soup.select_one(selector)
        if content_node is not None:
            break
    if content_node is None:
        raise ValueError(f"Could not extract article body from {source_url}")

    content = content_node.get_text(separator="\n\n", strip=True)
    if not content:
        raise ValueError(f"Article body is empty at {source_url}")

    summary = meta_content(soup, property_name="og:description")
    author = (
        first_text(soup, "a[rel='author']")
        or first_text(soup, ".author")
        or first_text(soup, "[itemprop='author']")
    )
    category = extract_category_from_meta(soup)
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
