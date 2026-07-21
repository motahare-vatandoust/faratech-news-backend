from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from crawler.registry import get_crawler, get_source_base_urls, list_sources
from core.scheduler import get_auto_crawler_status
from db.session import get_db
from models.auto_crawler import AutoCrawlerStatusResponse, AutoCrawlRunResponse
from models.crawler import CrawlRequest, CrawlResponse, CrawlerSourceInfo
from services import auto_crawler as auto_crawler_service
from services import crawler as crawler_service

router = APIRouter(prefix="/crawler", tags=["crawler"])

_SOURCE_BASE_URLS = get_source_base_urls()


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
        translate_to_farsi=request.translate_to_farsi,
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
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> CrawlResponse:
    """Crawl DZone, translate to Farsi, and save new articles to the news table."""
    result, saved_count = await crawler_service.sync_dzone(
        db, limit=limit, translate_to_farsi=translate_to_farsi
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/deepmind/sync", response_model=CrawlResponse)
async def sync_deepmind_news(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> CrawlResponse:
    """Crawl Google DeepMind blog, translate to Farsi, and save new articles."""
    result, saved_count = await crawler_service.sync_deepmind(
        db, limit=limit, translate_to_farsi=translate_to_farsi
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/hubspot/sync", response_model=CrawlResponse)
async def sync_hubspot_news(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> CrawlResponse:
    """Crawl HubSpot blog, translate to Farsi, and save new articles."""
    result, saved_count = await crawler_service.sync_hubspot(
        db, limit=limit, translate_to_farsi=translate_to_farsi
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/marketingweek/sync", response_model=CrawlResponse)
async def sync_marketingweek_news(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> CrawlResponse:
    """Crawl Marketing Week, translate to Farsi, and save new articles."""
    result, saved_count = await crawler_service.sync_marketingweek(
        db, limit=limit, translate_to_farsi=translate_to_farsi
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/rundown/sync", response_model=CrawlResponse)
async def sync_rundown_news(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> CrawlResponse:
    """Crawl The Rundown AI, translate to Farsi, and save new articles."""
    result, saved_count = await crawler_service.sync_rundown(
        db, limit=limit, translate_to_farsi=translate_to_farsi
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/bensbites/sync", response_model=CrawlResponse)
async def sync_bensbites_news(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> CrawlResponse:
    """Crawl Ben's Bites, translate to Farsi, and save new articles."""
    result, saved_count = await crawler_service.sync_bensbites(
        db, limit=limit, translate_to_farsi=translate_to_farsi
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/huggingface/sync", response_model=CrawlResponse)
async def sync_huggingface_news(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> CrawlResponse:
    """Crawl Hugging Face blog, translate to Farsi, and save new articles."""
    result, saved_count = await crawler_service.sync_huggingface(
        db, limit=limit, translate_to_farsi=translate_to_farsi
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/techcrunch/sync", response_model=CrawlResponse)
async def sync_techcrunch_news(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> CrawlResponse:
    """Crawl TechCrunch AI, translate to Farsi, and save new articles."""
    result, saved_count = await crawler_service.sync_techcrunch(
        db, limit=limit, translate_to_farsi=translate_to_farsi
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/anthropic/sync", response_model=CrawlResponse)
async def sync_anthropic_news(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> CrawlResponse:
    """Crawl Anthropic news, translate to Farsi, and save new articles."""
    result, saved_count = await crawler_service.sync_anthropic(
        db, limit=limit, translate_to_farsi=translate_to_farsi
    )

    return CrawlResponse(
        source=result.source,
        fetched_count=len(result.articles),
        saved_count=saved_count,
        skipped_count=len(result.skipped_urls),
        errors=result.errors,
        articles=result.articles,
    )


@router.post("/auto/run", response_model=AutoCrawlRunResponse)
async def run_auto_crawl(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    translate_to_farsi: bool = Query(
        default=True,
        description="Translate and clean articles to Farsi via GapGPT before saving",
    ),
) -> AutoCrawlRunResponse:
    """Run a crawl for all registered sources (used by the automatic scheduler too)."""
    return await auto_crawler_service.run_auto_crawl(
        db,
        limit=limit,
        translate_to_farsi=translate_to_farsi,
    )


@router.get("/status", response_model=AutoCrawlerStatusResponse)
def get_crawler_status() -> AutoCrawlerStatusResponse:
    """Return auto crawler scheduler runtime status."""
    return get_auto_crawler_status()
