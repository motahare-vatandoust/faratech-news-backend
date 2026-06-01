from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NewsBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class NewsCreate(NewsBase):
    pass


class NewsUpdate(NewsBase):
    pass


class NewsResponse(NewsBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
