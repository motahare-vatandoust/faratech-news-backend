from typing import Optional

from crawler.base import BaseCrawler
from crawler.config import CRAWLER_DEFAULT_LIMIT
from crawler.http_client import crawl_client, fetch_html
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

        async with crawl_client() as client:
            try:
                home_html = await fetch_html(client, config.HOME_URL)
            except Exception as exc:
                result.errors.append(f"Failed to fetch homepage: {exc}")
                return result

            article_urls = extract_article_urls(home_html)
            if max_articles > 0:
                article_urls = article_urls[:max_articles]

            for url in article_urls:
                try:
                    html = await fetch_html(client, url)
                    article = parse_article_page(html, url)
                    result.articles.append(article)
                except Exception as exc:
                    result.errors.append(f"{url}: {exc}")

        return result
