from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from crawler.schemas import CrawledArticle


class CrawlRequest(BaseModel):
    source: str = Field(default="dzone", description="Registered crawler source name")
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Maximum number of articles to fetch",
    )
    persist: bool = Field(
        default=True,
        description="When true, save new articles to the database",
    )


class CrawlResponse(BaseModel):
    source: str
    fetched_count: int
    saved_count: int
    skipped_count: int
    errors: list[str]
    articles: list[CrawledArticle]


class CrawlerSourceInfo(BaseModel):
    name: str
    base_url: str
