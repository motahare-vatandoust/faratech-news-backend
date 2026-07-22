from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, defer

from core.categories import category_filter_values, normalize_category
from crawler.metadata import resolve_category_and_tags
from db.models.news import News, NewsStatus
from models.news import NewsCreate, NewsPatch, NewsUpdate


def get_all_news(
    db: Session,
    *,
    status: Optional[NewsStatus] = None,
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> List[News]:
    stmt = (
        select(News)
        .options(defer(News.content))
        .order_by(News.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if status is not None:
        stmt = stmt.where(News.status == status)
    if category is not None:
        stmt = stmt.where(News.category.in_(category_filter_values(category)))
    return list(db.scalars(stmt).all())


def get_news_by_id(db: Session, news_id: UUID) -> Optional[News]:
    return db.get(News, news_id)


def create_news(db: Session, data: NewsCreate) -> News:
    category, tags = resolve_category_and_tags(
        source=data.source or "",
        category=data.category,
        tags=data.tags,
    )
    payload = data.model_dump()
    payload["category"] = category
    payload["tags"] = tags
    news = News(**payload)
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


def update_news(db: Session, news_id: UUID, data: NewsUpdate) -> Optional[News]:
    news = db.get(News, news_id)
    if news is None:
        return None

    payload = data.model_dump(exclude_unset=True)
    if "category" in payload and payload["category"] is not None:
        payload["category"] = normalize_category(payload["category"])
    for field, value in payload.items():
        setattr(news, field, value)

    db.commit()
    db.refresh(news)
    return news


def patch_news(db: Session, news_id: UUID, data: NewsPatch) -> Optional[News]:
    news = db.get(News, news_id)
    if news is None:
        return None

    payload = data.model_dump(exclude_unset=True)
    if "category" in payload and payload["category"] is not None:
        payload["category"] = normalize_category(payload["category"])
    for field, value in payload.items():
        setattr(news, field, value)

    db.commit()
    db.refresh(news)
    return news


def delete_news(db: Session, news_id: UUID) -> bool:
    news = db.get(News, news_id)
    if news is None:
        return False

    db.delete(news)
    db.commit()
    return True
