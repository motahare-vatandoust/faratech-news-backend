from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from crawler.registry import get_crawler, list_sources
from crawler.sources.dzone.crawler import DZoneCrawler
from db.session import get_db
from models.crawler import CrawlRequest, CrawlResponse, CrawlerSourceInfo
from services import crawler as crawler_service

router = APIRouter(prefix="/crawler", tags=["crawler"])

_SOURCE_BASE_URLS = {
    DZoneCrawler.source_name: DZoneCrawler.base_url,
}


@router.get("/sources", response_model=List[CrawlerSourceInfo])
def list_crawler_sources() -> List[CrawlerSourceInfo]:
    return [
        CrawlerSourceInfo(
            name=name,
            base_url=_SOURCE_BASE_URLS.get(name, ""),
        )
        for name in list_sources()
    ]


@router.post("/run", response_model=CrawlResponse)
async def run_crawler(
    request: CrawlRequest,
    db: Session = Depends(get_db),
) -> CrawlResponse:
    try:
        get_crawler(request.source)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    result, saved_count = await crawler_service.run_crawl(
        db,
        request.source,
        limit=request.limit,
        persist=request.persist,
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/dzone/sync", response_model=CrawlResponse)
async def sync_dzone_news(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
) -> CrawlResponse:
    """Crawl DZone for new articles and save them to the news table."""
    result, saved_count = await crawler_service.sync_dzone(db, limit=limit)

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )
