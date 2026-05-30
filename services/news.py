from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.news import News
from models.news import NewsCreate, NewsUpdate


def get_all_news(db: Session) -> List[News]:
    stmt = select(News).order_by(News.created_at.desc())
    return list(db.scalars(stmt).all())


def get_news_by_id(db: Session, news_id: UUID) -> Optional[News]:
    return db.get(News, news_id)


def create_news(db: Session, data: NewsCreate) -> News:
    news = News(**data.model_dump())
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


def update_news(db: Session, news_id: UUID, data: NewsUpdate) -> Optional[News]:
    news = db.get(News, news_id)
    if news is None:
        return None

    for field, value in data.model_dump().items():
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
