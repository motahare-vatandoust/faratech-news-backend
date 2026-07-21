from typing import Optional

from crawler.base import BaseCrawler
from crawler.config import CRAWLER_DEFAULT_LIMIT
from crawler.http_client import crawl_client, fetch_html, format_request_error
from crawler.schemas import CrawlResult
from crawler.sources.creativebloq import config
from crawler.sources.creativebloq.parser import (
    extract_article_urls_from_feed,
    extract_title_map_from_feed,
    parse_article_page,
)


class CreativeBloqCrawler(BaseCrawler):
    """Crawls design and creative industry news from Creative Bloq."""

    source_name = "creativebloq"
    base_url = config.BASE_URL

    async def crawl(self, *, limit: Optional[int] = None) -> CrawlResult:
        max_articles = limit if limit is not None else CRAWLER_DEFAULT_LIMIT
        result = CrawlResult(source=self.source_name)

        async with crawl_client() as fetcher:
            try:
                feed_xml = await fetch_html(fetcher, config.FEED_URL)
            except Exception as exc:
                result.errors.append(
                    "Failed to fetch feed: "
                    + format_request_error(exc, url=config.FEED_URL)
                )
                return result

            article_urls = extract_article_urls_from_feed(feed_xml)
            if not article_urls:
                result.errors.append(
                    "No article links found in Creative Bloq RSS feed."
                )
                return result

            if max_articles > 0:
                article_urls = article_urls[:max_articles]

            title_map = extract_title_map_from_feed(feed_xml)

            for url in article_urls:
                try:
                    html = await fetch_html(fetcher, url)
                    article = parse_article_page(
                        html,
                        url,
                        fallback_title=title_map.get(url.rstrip("/")),
                    )
                    result.articles.append(article)
                except Exception as exc:
                    result.errors.append(format_request_error(exc, url=url))

        return result
