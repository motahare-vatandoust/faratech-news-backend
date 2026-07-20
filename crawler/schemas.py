from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class CrawledArticle(BaseModel):
    """Normalized article payload produced by any source crawler."""

    title: str
    content: str
    source_url: HttpUrl
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    cover_image_url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None


class CrawlResult(BaseModel):
    """Outcome of a single crawl run for one source."""

    source: str
    articles: list[CrawledArticle] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    skipped_urls: list[str] = Field(default_factory=list)
