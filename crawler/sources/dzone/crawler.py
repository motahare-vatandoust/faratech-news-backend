from typing import Optional

from crawler.base import BaseCrawler
from crawler.config import CRAWLER_DEFAULT_LIMIT
from crawler.http_client import (
    crawl_client,
    fetch_html,
    format_request_error,
    is_cloudflare_block,
)
from crawler.schemas import CrawlResult
from crawler.sources.dzone import config
from crawler.sources.dzone.parser import extract_article_urls, parse_article_page


class DZoneCrawler(BaseCrawler):
    """Crawls article listings from dzone.com and fetches full article content."""

    source_name = "dzone"
    base_url = config.BASE_URL

    async def crawl(self, *, limit: Optional[int] = None) -> CrawlResult:
        max_articles = limit if limit is not None else CRAWLER_DEFAULT_LIMIT
        result = CrawlResult(source=self.source_name)

        async with crawl_client() as fetcher:
            try:
                home_html = await fetch_html(fetcher, config.HOME_URL)
            except Exception as exc:
                result.errors.append(
                    "Failed to fetch homepage: "
                    + format_request_error(exc, url=config.HOME_URL)
                )
                return result

            if is_cloudflare_block(status_code=200, html=home_html):
                result.errors.append(
                    "DZone returned a Cloudflare challenge page (HTTP 403 from curl). "
                    "Install curl_cffi, use a VPN, or try: pip install curl_cffi"
                )
                return result

            article_urls = extract_article_urls(home_html)
            if not article_urls:
                result.errors.append(
                    "No article links found on the homepage. "
                    "DZone may be blocking automated access from your network."
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
