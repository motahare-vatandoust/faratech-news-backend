from abc import ABC, abstractmethod
from typing import Optional

from crawler.schemas import CrawlResult


class BaseCrawler(ABC):
    """Contract for site-specific crawlers."""

    source_name: str
    base_url: str

    @abstractmethod
    async def crawl(self, *, limit: Optional[int] = None) -> CrawlResult:
        """Discover and fetch articles from the configured source."""
