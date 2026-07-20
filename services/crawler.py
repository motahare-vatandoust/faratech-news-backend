import asyncio
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from crawler.metadata import resolve_category_and_tags
from crawler.registry import get_crawler
from crawler.schemas import CrawlResult, CrawledArticle
from db.models.news import News
from models.news import NewsCreate, NewsStatus
from services import news as news_service
from services.article_translator import translate_article_to_farsi


def _article_to_news_create(article: CrawledArticle, source: str) -> NewsCreate:
    category, tags = resolve_category_and_tags(
        source=source,
        category=article.category,
        tags=article.tags,
    )
    return NewsCreate(
        title=article.title,
        content=article.content,
        summary=article.summary,
        category=category,
        tags=tags,
        source=source,
        source_url=str(article.source_url),
        cover_image_url=article.cover_image_url,
        status=NewsStatus.draft,
    )


async def _translate_crawled_article(article: CrawledArticle) -> CrawledArticle:
    translated = await asyncio.to_thread(
        translate_article_to_farsi,
        title=article.title,
        content=article.content,
        summary=article.summary,
    )
    return article.model_copy(
        update={
            "title": translated.title,
            "content": translated.content,
            "summary": translated.summary,
            "category": translated.category or article.category,
            "tags": translated.tags or article.tags,
        }
    )


async def _apply_farsi_translation(result: CrawlResult) -> None:
    translated_articles: list[CrawledArticle] = []
    for article in result.articles:
        source_url = str(article.source_url)
        try:
            translated_articles.append(await _translate_crawled_article(article))
        except Exception as exc:
            result.errors.append(f"{source_url}: translation failed: {exc}")
            translated_articles.append(article)
    result.articles = translated_articles


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

    if translate_to_farsi:
        await _apply_farsi_translation(result)

    if not persist:
        return result, 0

    saved_count = 0
    for article in result.articles:
        source_url = str(article.source_url)
        if _find_existing(db, source, source_url) is not None:
            result.skipped_urls.append(source_url)
            continue

        try:
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


async def sync_deepmind(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> tuple[CrawlResult, int]:
    """Fetch new Google DeepMind blog articles, translate to Farsi, and persist."""
    return await run_crawl(
        db,
        "deepmind",
        limit=limit,
        persist=True,
        translate_to_farsi=translate_to_farsi,
    )


async def sync_hubspot(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> tuple[CrawlResult, int]:
    """Fetch new HubSpot blog articles, translate to Farsi, and persist."""
    return await run_crawl(
        db,
        "hubspot",
        limit=limit,
        persist=True,
        translate_to_farsi=translate_to_farsi,
    )


async def sync_marketingweek(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> tuple[CrawlResult, int]:
    """Fetch new Marketing Week posts, translate to Farsi, and persist."""
    return await run_crawl(
        db,
        "marketingweek",
        limit=limit,
        persist=True,
        translate_to_farsi=translate_to_farsi,
    )


async def sync_rundown(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> tuple[CrawlResult, int]:
    """Fetch new Rundown AI posts, translate to Farsi, and persist."""
    return await run_crawl(
        db,
        "rundown",
        limit=limit,
        persist=True,
        translate_to_farsi=translate_to_farsi,
    )


async def sync_bensbites(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> tuple[CrawlResult, int]:
    """Fetch new Ben's Bites posts, translate to Farsi, and persist."""
    return await run_crawl(
        db,
        "bensbites",
        limit=limit,
        persist=True,
        translate_to_farsi=translate_to_farsi,
    )


async def sync_huggingface(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> tuple[CrawlResult, int]:
    """Fetch new Hugging Face blog posts, translate to Farsi, and persist."""
    return await run_crawl(
        db,
        "huggingface",
        limit=limit,
        persist=True,
        translate_to_farsi=translate_to_farsi,
    )


async def sync_techcrunch(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> tuple[CrawlResult, int]:
    """Fetch new TechCrunch AI articles, translate to Farsi, and persist."""
    return await run_crawl(
        db,
        "techcrunch",
        limit=limit,
        persist=True,
        translate_to_farsi=translate_to_farsi,
    )


async def sync_anthropic(
    db: Session,
    *,
    limit: Optional[int] = None,
    translate_to_farsi: bool = True,
) -> tuple[CrawlResult, int]:
    """Fetch new Anthropic news posts, translate to Farsi, and persist."""
    return await run_crawl(
        db,
        "anthropic",
        limit=limit,
        persist=True,
        translate_to_farsi=translate_to_farsi,
    )
