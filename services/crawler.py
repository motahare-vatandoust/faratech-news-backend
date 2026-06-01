from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from crawler.registry import get_crawler
from crawler.schemas import CrawlResult, CrawledArticle
from db.models.news import News
from models.news import NewsCreate
from services import news as news_service


def _article_to_news_create(article: CrawledArticle, source: str) -> NewsCreate:
    return NewsCreate(
        title=article.title,
        content=article.content,
        summary=article.summary,
        source=source,
        source_url=str(article.source_url),
    )


def _find_existing(db: Session, source: str, source_url: str) -> Optional[News]:
    stmt = select(News).where(News.source == source, News.source_url == source_url)
    return db.scalars(stmt).first()


async def run_crawl(
    db: Session,
    source: str,
    *,
    limit: Optional[int] = None,
    persist: bool = True,
) -> tuple[CrawlResult, int]:
    crawler = get_crawler(source)
    result = await crawler.crawl(limit=limit)

    if not persist:
        return result, 0

    saved_count = 0
    for article in result.articles:
        source_url = str(article.source_url)
        if _find_existing(db, source, source_url) is not None:
            result.skipped_urls.append(source_url)
            continue

        news_service.create_news(db, _article_to_news_create(article, source))
        saved_count += 1

    return result, saved_count


async def sync_dzone(
    db: Session,
    *,
    limit: Optional[int] = None,
) -> tuple[CrawlResult, int]:
    """Fetch new DZone articles and persist them with source='dzone'."""
    return await run_crawl(db, "dzone", limit=limit, persist=True)
