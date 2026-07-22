"""Reusable BaseCrawler for sources that discover articles via RSS/Atom."""

from __future__ import annotations

from typing import Callable, Optional

from crawler.base import BaseCrawler
from crawler.config import CRAWLER_DEFAULT_LIMIT
from crawler.http_client import crawl_client, fetch_html, format_request_error
from crawler.rss import (
    extract_article_urls_from_feed,
    extract_title_map_from_feed,
    parse_generic_article_page,
)
from crawler.schemas import CrawlResult, CrawledArticle

ParseArticle = Callable[..., CrawledArticle]
NormalizeUrl = Callable[[str], Optional[str]]


class RssFeedCrawler(BaseCrawler):
    """Subclass and set source_name, base_url, feed_url, normalize_url."""

    feed_url: str
    normalize_url: NormalizeUrl
    feed_label: str = "RSS"
    parse_article: ParseArticle = staticmethod(parse_generic_article_page)

    async def crawl(self, *, limit: Optional[int] = None) -> CrawlResult:
        max_articles = limit if limit is not None else CRAWLER_DEFAULT_LIMIT
        result = CrawlResult(source=self.source_name)

        async with crawl_client() as fetcher:
            try:
                feed_xml = await fetch_html(fetcher, self.feed_url)
            except Exception as exc:
                result.errors.append(
                    "Failed to fetch feed: "
                    + format_request_error(exc, url=self.feed_url)
                )
                return result

            article_urls = extract_article_urls_from_feed(
                feed_xml,
                normalize_url=self.normalize_url,
            )
            if not article_urls:
                result.errors.append(
                    f"No article links found in {self.feed_label} feed."
                )
                return result

            if max_articles > 0:
                article_urls = article_urls[:max_articles]

            title_map = extract_title_map_from_feed(
                feed_xml,
                normalize_url=self.normalize_url,
            )

            for url in article_urls:
                try:
                    html = await fetch_html(fetcher, url)
                    article = self.parse_article(
                        html,
                        url,
                        fallback_title=title_map.get(url.rstrip("/")),
                    )
                    result.articles.append(article)
                except Exception as exc:
                    result.errors.append(format_request_error(exc, url=url))

        return result
