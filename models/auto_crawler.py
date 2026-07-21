from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AutoCrawlRunResponse(BaseModel):
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    success_count: int
    failed_count: int
    exceptions: List[str] = Field(default_factory=list)


class AutoCrawlerStatusResponse(BaseModel):
    scheduler_running: bool
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    last_duration: Optional[float] = None
    last_success: Optional[bool] = None
    failed_sources: List[str] = Field(default_factory=list)
