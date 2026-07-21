import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from crawler.registry import list_sources
from models.auto_crawler import AutoCrawlRunResponse
from services import crawler as crawler_service

logger = logging.getLogger(__name__)


async def run_auto_crawl(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> AutoCrawlRunResponse:
    """
    Crawl all registered crawler sources and persist any new articles.

    This reuses the existing crawler + persistence flow from
    `services.crawler.run_crawl` (and therefore the existing manual endpoints),
    without duplicating crawling logic.
    """

    started_at = datetime.now(timezone.utc)
    success_count = 0
    failed_count = 0
    exceptions: list[str] = []

    for source in list_sources():
        try:
            result, _saved_count = await crawler_service.run_crawl(
                db,
                source,
                limit=limit,
                persist=True,
                translate_to_farsi=translate_to_farsi,
            )

            if result.errors:
                failed_count += 1
                # These are surfaced as strings today; log them in the scheduler too.
                exceptions.extend([f"{source}: {err}" for err in result.errors])
            else:
                success_count += 1
        except Exception as exc:
            failed_count += 1
            msg = f"{source}: {type(exc).__name__}: {exc}"
            exceptions.append(msg)
            logger.exception("Auto crawl failed for source=%s", source, exc_info=exc)

    finished_at = datetime.now(timezone.utc)
    duration_seconds = (finished_at - started_at).total_seconds()

    return AutoCrawlRunResponse(
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
        success_count=success_count,
        failed_count=failed_count,
        exceptions=exceptions,
    )

