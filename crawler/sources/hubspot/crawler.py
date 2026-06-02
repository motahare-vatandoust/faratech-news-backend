from typing import Optional

from crawler.base import BaseCrawler
from crawler.config import CRAWLER_DEFAULT_LIMIT
from crawler.http_client import crawl_client, fetch_html, format_request_error
from crawler.schemas import CrawlResult
from crawler.sources.hubspot import config
from crawler.sources.hubspot.parser import extract_article_urls, parse_article_page


class HubSpotCrawler(BaseCrawler):
    """Crawls articles from the HubSpot Blog marketing/news sections."""

    source_name = "hubspot"
    base_url = config.BASE_URL

    async def crawl(self, *, limit: Optional[int] = None) -> CrawlResult:
        max_articles = limit if limit is not None else CRAWLER_DEFAULT_LIMIT
        result = CrawlResult(source=self.source_name)

        async with crawl_client() as fetcher:
            try:
                blog_html = await fetch_html(fetcher, config.BLOG_URL)
            except Exception as exc:
                result.errors.append(
                    "Failed to fetch blog listing: "
                    + format_request_error(exc, url=config.BLOG_URL)
                )
                return result

            article_urls = extract_article_urls(blog_html)
            if not article_urls:
                result.errors.append("No article links found on HubSpot blog homepage.")
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
