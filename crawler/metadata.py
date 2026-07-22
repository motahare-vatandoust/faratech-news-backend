from typing import Optional, Union
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from core.categories import DEFAULT_CATEGORY, normalize_category

SOURCE_DEFAULTS: dict[str, dict[str, Union[str, list[str]]]] = {
    "dzone": {"category": "programming", "tags": ["programming"]},
    "deepmind": {"category": "ai", "tags": ["research", "machine learning"]},
    "hubspot": {"category": "marketing", "tags": ["marketing"]},
    "marketingweek": {"category": "marketing", "tags": ["marketing"]},
    "rundown": {"category": "ai", "tags": ["artificial intelligence"]},
    "bensbites": {"category": "ai", "tags": ["artificial intelligence"]},
    "huggingface": {"category": "ai", "tags": ["machine learning", "open source"]},
    "techcrunch": {"category": "ai", "tags": ["artificial intelligence", "startups"]},
    "anthropic": {"category": "ai", "tags": ["research", "artificial intelligence"]},
    "smashingmagazine": {"category": "design", "tags": ["design", "ux"]},
    "nngroup": {"category": "design", "tags": ["ux", "research"]},
    "designmilk": {"category": "design", "tags": ["design", "product design"]},
    "creativebloq": {"category": "design", "tags": ["design", "creative"]},
    "itsnicethat": {"category": "design", "tags": ["design", "creative"]},
}


def extract_tags_from_soup(soup: BeautifulSoup, *, limit: int = 10) -> list[str]:
    tags: list[str] = []
    seen: set[str] = set()

    for meta in soup.find_all("meta", attrs={"property": "article:tag"}):
        if not isinstance(meta, Tag):
            continue
        content = meta.get("content")
        if not content:
            continue
        tag = str(content).strip()
        key = tag.lower()
        if tag and key not in seen:
            seen.add(key)
            tags.append(tag)

    keywords_meta = soup.find("meta", attrs={"name": "keywords"})
    if isinstance(keywords_meta, Tag) and keywords_meta.get("content"):
        for part in str(keywords_meta["content"]).split(","):
            tag = part.strip()
            key = tag.lower()
            if tag and key not in seen:
                seen.add(key)
                tags.append(tag)

    for anchor in soup.select("a[rel='tag'], .article-tags a, .tag-list a, .tags a"):
        tag = anchor.get_text(strip=True)
        key = tag.lower()
        if tag and key not in seen:
            seen.add(key)
            tags.append(tag)

    return tags[:limit]


def extract_category_from_meta(soup: BeautifulSoup) -> Optional[str]:
    for prop in ("article:section", "og:article:section"):
        tag = soup.find("meta", attrs={"property": prop})
        if isinstance(tag, Tag) and tag.get("content"):
            value = str(tag["content"]).strip()
            if value:
                return value
    return None


def extract_cover_image_url(
    soup: BeautifulSoup,
    *,
    base_url: Optional[str] = None,
) -> Optional[str]:
    """Extract a cover/hero image URL from Open Graph, Twitter, or link tags."""

    candidates: list[str] = []

    for prop in ("og:image", "og:image:url", "og:image:secure_url"):
        tag = soup.find("meta", attrs={"property": prop})
        if isinstance(tag, Tag) and tag.get("content"):
            candidates.append(str(tag["content"]).strip())

    for name in ("twitter:image", "twitter:image:src"):
        tag = soup.find("meta", attrs={"name": name})
        if isinstance(tag, Tag) and tag.get("content"):
            candidates.append(str(tag["content"]).strip())
        tag = soup.find("meta", attrs={"property": name})
        if isinstance(tag, Tag) and tag.get("content"):
            candidates.append(str(tag["content"]).strip())

    link = soup.find("link", attrs={"rel": "image_src"})
    if isinstance(link, Tag) and link.get("href"):
        candidates.append(str(link["href"]).strip())

    for raw in candidates:
        if not raw:
            continue
        absolute = urljoin(base_url, raw) if base_url else raw
        if absolute.startswith(("http://", "https://")):
            return absolute

    return None


def resolve_category_and_tags(
    *,
    source: str,
    category: Optional[str],
    tags: Optional[list[str]],
) -> tuple[str, list[str]]:
    defaults = SOURCE_DEFAULTS.get(source, {})
    resolved_category = category or defaults.get("category")
    if not isinstance(resolved_category, str) or not resolved_category:
        resolved_category = DEFAULT_CATEGORY
    resolved_category = normalize_category(resolved_category)

    resolved_tags = list(tags) if tags else []
    if not resolved_tags:
        default_tags = defaults.get("tags", [])
        if isinstance(default_tags, list):
            resolved_tags = list(default_tags)

    return resolved_category, resolved_tags
