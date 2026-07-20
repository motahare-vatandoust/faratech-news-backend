from typing import Optional, Union

from bs4 import BeautifulSoup, Tag

SOURCE_DEFAULTS: dict[str, dict[str, Union[str, list[str]]]] = {
    "dzone": {"category": "Development", "tags": ["programming"]},
    "deepmind": {"category": "AI", "tags": ["research", "machine learning"]},
    "hubspot": {"category": "Marketing", "tags": ["marketing"]},
    "marketingweek": {"category": "Marketing", "tags": ["marketing"]},
    "rundown": {"category": "AI", "tags": ["artificial intelligence"]},
    "bensbites": {"category": "AI", "tags": ["artificial intelligence"]},
    "huggingface": {"category": "AI", "tags": ["machine learning", "open source"]},
    "techcrunch": {"category": "AI", "tags": ["artificial intelligence", "startups"]},
    "anthropic": {"category": "AI", "tags": ["research", "artificial intelligence"]},
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


def resolve_category_and_tags(
    *,
    source: str,
    category: Optional[str],
    tags: Optional[list[str]],
) -> tuple[str, list[str]]:
    defaults = SOURCE_DEFAULTS.get(source, {})
    resolved_category = category or defaults.get("category")
    if not isinstance(resolved_category, str) or not resolved_category:
        resolved_category = "General"

    resolved_tags = list(tags) if tags else []
    if not resolved_tags:
        default_tags = defaults.get("tags", [])
        if isinstance(default_tags, list):
            resolved_tags = list(default_tags)

    return resolved_category, resolved_tags
