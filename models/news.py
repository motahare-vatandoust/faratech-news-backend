from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NewsStatus(str, Enum):
    draft = "draft"
    review = "review"
    published = "published"


class NewsBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    cover_image_url: Optional[str] = None


class NewsCreate(NewsBase):
    status: NewsStatus = Field(default=NewsStatus.draft)


class NewsUpdate(NewsBase):
    status: Optional[NewsStatus] = None


class NewsPatch(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    status: Optional[NewsStatus] = None


class NewsListItem(BaseModel):
    """Lightweight list item — excludes full article body."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    status: NewsStatus
    created_at: datetime
    updated_at: datetime


class NewsResponse(NewsBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: NewsStatus
    created_at: datetime
    updated_at: datetime
