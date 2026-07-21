import asyncio
import logging
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator, Optional
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from core.config import AUTO_CRAWLER_ENABLED, CRAWLER_INTERVAL_MINUTES
from db.session import engine
from db.session import get_db
from models.auto_crawler import AutoCrawlerStatusResponse
from services import auto_crawler as auto_crawler_service

logger = logging.getLogger(__name__)

# In-process overlap protection (in addition to DB advisory lock).
_running_lock = threading.Lock()

# 64-bit signed integer for Postgres advisory locks.
_ADVISORY_LOCK_KEY = int.from_bytes(b"faratech_auto_crawler_v1", "big") % (
    2**63 - 1
)
_SCHEDULER_LEADER_LOCK_KEY = int.from_bytes(b"faratech_scheduler_leader_v1", "big") % (
    2**63 - 1
)

UTC = ZoneInfo("UTC")

_scheduler: Optional[BackgroundScheduler] = None
_leader_lock_connection: Optional[Connection] = None

_status_lock = threading.Lock()
_last_run: datetime | None = None
_last_duration: float | None = None
_last_success: bool | None = None
_failed_sources: list[str] = []


@contextmanager
def _db_session() -> Generator[Session, None, None]:
    db_gen = get_db()
    db = next(db_gen)
    try:
        yield db
    finally:
        # Ensure the session is always closed (mirrors FastAPI dependency behavior).
        db_gen.close()


def _try_acquire_advisory_lock(db: Session) -> bool:
    # Returns a single boolean column.
    locked = db.execute(
        text("SELECT pg_try_advisory_lock(:key)"),
        {"key": _ADVISORY_LOCK_KEY},
    ).scalar()
    return bool(locked)


def _release_advisory_lock(db: Session) -> None:
    db.execute(
        text("SELECT pg_advisory_unlock(:key)"),
        {"key": _ADVISORY_LOCK_KEY},
    )


def _try_acquire_scheduler_leader_lock() -> Optional[Connection]:
    conn = engine.connect()
    lock_acquired = conn.execute(
        text("SELECT pg_try_advisory_lock(:key)"),
        {"key": _SCHEDULER_LEADER_LOCK_KEY},
    ).scalar()
    if lock_acquired:
        return conn
    conn.close()
    return None


def _release_scheduler_leader_lock(connection: Connection) -> None:
    try:
        connection.execute(
            text("SELECT pg_advisory_unlock(:key)"),
            {"key": _SCHEDULER_LEADER_LOCK_KEY},
        )
    finally:
        connection.close()


def _extract_failed_sources(exceptions: list[str]) -> list[str]:
    sources: set[str] = set()
    for message in exceptions:
        source = message.split(":", 1)[0].strip()
        if source:
            sources.add(source)
    return sorted(sources)


def _auto_crawl_job() -> None:
    global _last_run, _last_duration, _last_success, _failed_sources

    # Skip if a previous run is still running in this process.
    if not _running_lock.acquire(blocking=False):
        logger.warning("Auto crawl skipped: previous run still active in this process.")
        return

    advisory_lock_acquired = False
    with _db_session() as db:
        try:
            advisory_lock_acquired = _try_acquire_advisory_lock(db)
            if not advisory_lock_acquired:
                logger.warning(
                    "Auto crawl skipped: another worker/process currently holds crawl lock."
                )
                return

            started_at = datetime.now(UTC)
            logger.info("Auto crawl started at %s (UTC).", started_at.isoformat())
            summary = asyncio.run(auto_crawler_service.run_auto_crawl(db))
            logger.info(
                "Auto crawl finished: start=%s finish=%s duration_seconds=%.3f success_websites=%d failed_websites=%d",
                summary.started_at.isoformat(),
                summary.finished_at.isoformat(),
                summary.duration_seconds,
                summary.success_count,
                summary.failed_count,
            )

            failed_sources = _extract_failed_sources(summary.exceptions)
            with _status_lock:
                _last_run = summary.finished_at
                _last_duration = summary.duration_seconds
                _last_success = summary.failed_count == 0 and len(summary.exceptions) == 0
                _failed_sources = failed_sources

            if summary.exceptions:
                for exc_msg in summary.exceptions:
                    logger.error("Auto crawl source failure: %s", exc_msg)
            else:
                logger.info("Auto crawl completed without source-level errors.")
        except Exception:
            # Log any unexpected exception (includes tracebacks).
            with _status_lock:
                _last_run = datetime.now(UTC)
                _last_duration = None
                _last_success = False
                _failed_sources = ["job"]
            logger.exception("Auto crawl job failed unexpectedly.")
        finally:
            if advisory_lock_acquired:
                try:
                    _release_advisory_lock(db)
                except Exception:
                    logger.exception("Failed to release auto crawl advisory lock.")
            _running_lock.release()


def start_auto_crawler_scheduler() -> Optional[BackgroundScheduler]:
    global _scheduler, _leader_lock_connection
    if _scheduler is not None:
        return _scheduler

    if not AUTO_CRAWLER_ENABLED:
        logger.info(
            "Auto crawler scheduler disabled by configuration: AUTO_CRAWLER_ENABLED=false."
        )
        return None

    _leader_lock_connection = _try_acquire_scheduler_leader_lock()
    if _leader_lock_connection is None:
        logger.info(
            "Scheduler not started in this worker: another worker is the scheduler leader."
        )
        return None

    interval_minutes = CRAWLER_INTERVAL_MINUTES

    scheduler = BackgroundScheduler(timezone=UTC)
    scheduler.add_job(
        _auto_crawl_job,
        trigger=IntervalTrigger(minutes=interval_minutes, timezone=UTC),
        id="auto_crawl_job",
        name="Auto crawl (all sources)",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=300,
    )
    scheduler.start()

    _scheduler = scheduler
    logger.info(
        "Auto crawler scheduler started in leader worker: interval=%d minute(s), timezone=UTC, coalesce=True, max_instances=1, misfire_grace_time=300.",
        interval_minutes,
    )
    return scheduler


def shutdown_auto_crawler_scheduler(
    scheduler: Optional[BackgroundScheduler],
) -> None:
    global _scheduler, _leader_lock_connection

    if scheduler is None:
        if _leader_lock_connection is not None:
            try:
                _release_scheduler_leader_lock(_leader_lock_connection)
            except Exception:
                logger.exception("Failed to release scheduler leader advisory lock.")
            finally:
                _leader_lock_connection = None
        return

    try:
        scheduler.shutdown(wait=False)
        logger.info("Auto crawler scheduler shutdown completed.")
    except Exception:
        logger.exception("Failed to shutdown auto crawler scheduler.")
    finally:
        _scheduler = None
        if _leader_lock_connection is not None:
            try:
                _release_scheduler_leader_lock(_leader_lock_connection)
            except Exception:
                logger.exception("Failed to release scheduler leader advisory lock.")
            finally:
                _leader_lock_connection = None


def get_auto_crawler_status() -> AutoCrawlerStatusResponse:
    scheduler_running = _scheduler is not None and _scheduler.running
    next_run = None
    if scheduler_running:
        job = _scheduler.get_job("auto_crawl_job")
        if job is not None and job.next_run_time is not None:
            next_run = job.next_run_time.astimezone(UTC)

    with _status_lock:
        return AutoCrawlerStatusResponse(
            scheduler_running=scheduler_running,
            next_run=next_run,
            last_run=_last_run,
            last_duration=_last_duration,
            last_success=_last_success,
            failed_sources=list(_failed_sources),
        )

