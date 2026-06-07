from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, defer

from crawler.metadata import resolve_category_and_tags
from db.models.news import News, NewsStatus
from models.news import NewsCreate, NewsPatch, NewsUpdate


def get_all_news(
    db: Session,
    *,
    status: Optional[NewsStatus] = None,
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
    for field, value in payload.items():
        setattr(news, field, value)

    db.commit()
    db.refresh(news)
    return news


def patch_news(db: Session, news_id: UUID, data: NewsPatch) -> Optional[News]:
    news = db.get(News, news_id)
    if news is None:
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
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
