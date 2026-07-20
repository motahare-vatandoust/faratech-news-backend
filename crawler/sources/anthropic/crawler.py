from typing import Optional

from crawler.base import BaseCrawler
from crawler.config import CRAWLER_DEFAULT_LIMIT
from crawler.http_client import crawl_client, fetch_html, format_request_error
from crawler.schemas import CrawlResult
from crawler.sources.anthropic import config
from crawler.sources.anthropic.parser import extract_article_urls, parse_article_page


class AnthropicCrawler(BaseCrawler):
    """Crawls articles from the Anthropic news page."""

    source_name = "anthropic"
    base_url = config.BASE_URL

    async def crawl(self, *, limit: Optional[int] = None) -> CrawlResult:
        max_articles = limit if limit is not None else CRAWLER_DEFAULT_LIMIT
        result = CrawlResult(source=self.source_name)

        async with crawl_client() as fetcher:
            try:
                listing_html = await fetch_html(fetcher, config.NEWS_URL)
            except Exception as exc:
                result.errors.append(
                    "Failed to fetch news listing: "
                    + format_request_error(exc, url=config.NEWS_URL)
                )
                return result

            article_urls = extract_article_urls(listing_html)
            if not article_urls:
                result.errors.append(
                    "No article links found on the Anthropic news page."
                )
                return result

            if max_articles > 0:
                article_urls = article_urls[:max_articles]

            for url in article_urls:
                try:
                    html = await fetch_html(fetcher, url)
                    article = parse_article_page(html, url)
                    result.articles.append(article)
                except Exception as exc:
                    result.errors.append(format_request_error(exc, url=url))

        return result
