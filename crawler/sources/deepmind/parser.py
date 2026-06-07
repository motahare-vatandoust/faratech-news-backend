from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from crawler.metadata import extract_category_from_meta, extract_tags_from_soup
from crawler.schemas import CrawledArticle
from crawler.sources.deepmind import config


def _normalize_article_url(href: str) -> Optional[str]:
    if not href or href.startswith("#"):
        return None

    absolute = urljoin(config.BASE_URL, href.split("?")[0].rstrip("/"))
    parsed = urlparse(absolute)

    if parsed.netloc not in config.ALLOWED_HOSTS:
        return None

    path = parsed.path.rstrip("/")
    if not path.startswith(config.ARTICLE_PATH_PREFIX):
        return None

    slug = path[len(config.ARTICLE_PATH_PREFIX) :]
    if not slug:
        return None

    return f"{config.BASE_URL}{path}"


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
    body = soup.select_one('[data-component="uni-article-body"]')
    if body is not None:
        text = body.get_text(separator="\n\n", strip=True)
        if text:
            return text

    main = soup.select_one("main")
    if main is not None:
        rich_blocks = main.select(".rich-text")
        if rich_blocks:
            parts = [
                block.get_text(separator="\n\n", strip=True)
                for block in rich_blocks
                if block.get_text(strip=True)
            ]
            if parts:
                return "\n\n".join(parts)

        text = main.get_text(separator="\n\n", strip=True)
        if text:
            return text

    return None


def parse_article_page(html: str, source_url: str) -> CrawledArticle:
    soup = BeautifulSoup(html, "html.parser")

    title = (
        _first_text(soup, "h1.article-hero__h1")
        or _first_text(soup, "h1")
        or _meta_content(soup, property_name="og:title")
    )
    if not title:
        raise ValueError(f"Could not extract title from {source_url}")

    content = _extract_content(soup)
    if not content:
        raise ValueError(f"Could not extract article body from {source_url}")

    summary = (
        _first_text(soup, ".article-meta__abstract-text")
        or _meta_content(soup, property_name="og:description")
    )
    author = _first_text(soup, ".article-meta__author-name")
    category = extract_category_from_meta(soup) or _first_text(soup, ".article-meta__category")
    tags = extract_tags_from_soup(soup)

    return CrawledArticle(
        title=title,
        content=content,
        summary=summary,
        category=category,
        tags=tags or None,
        source_url=source_url,
        author=author,
    )
