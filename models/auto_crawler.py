from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class AutoCrawlRunResponse(BaseModel):
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    success_count: int
    failed_count: int
    exceptions: list[str] = Field(default_factory=list)


class AutoCrawlerStatusResponse(BaseModel):
    scheduler_running: bool
    next_run: datetime | None = None
    last_run: datetime | None = None
    last_duration: float | None = None
    last_success: bool | None = None
    failed_sources: list[str] = Field(default_factory=list)

