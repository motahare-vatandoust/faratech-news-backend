import asyncio
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from crawler.registry import get_crawler
from crawler.schemas import CrawlResult, CrawledArticle
from db.models.news import News
from models.news import NewsCreate
from services import news as news_service
from services.article_translator import translate_article_to_farsi


def _article_to_news_create(article: CrawledArticle, source: str) -> NewsCreate:
    return NewsCreate(
        title=article.title,
        content=article.content,
        summary=article.summary,
        source=source,
        source_url=str(article.source_url),
    )


async def _article_to_farsi_news_create(
    article: CrawledArticle, source: str
) -> NewsCreate:
    translated = await asyncio.to_thread(
        translate_article_to_farsi,
        title=article.title,
        content=article.content,
        summary=article.summary,
    )
    return NewsCreate(
        title=translated.title,
        content=translated.content,
        summary=translated.summary,
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
    translate_to_farsi: bool = False,
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

        try:
            if translate_to_farsi:
                news_data = await _article_to_farsi_news_create(article, source)
            else:
                news_data = _article_to_news_create(article, source)
            news_service.create_news(db, news_data)
            saved_count += 1
        except Exception as exc:
            result.errors.append(f"{source_url}: {exc}")

    return result, saved_count


async def sync_dzone(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> tuple[CrawlResult, int]:
    """Fetch new DZone articles, translate to Farsi, and persist."""
    return await run_crawl(
        db,
        "dzone",
        limit=limit,
        persist=True,
        translate_to_farsi=translate_to_farsi,
    )
