from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.models.news import NewsStatus
from db.session import get_db
from models.news import NewsCreate, NewsPatch, NewsResponse, NewsUpdate
from services import news as news_service

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=List[NewsResponse])
def list_news(
    db: Session = Depends(get_db),
    status: Optional[NewsStatus] = Query(default=None),
) -> List[NewsResponse]:
    return news_service.get_all_news(db, status=status)


@router.get("/{news_id}", response_model=NewsResponse)
def get_news(news_id: UUID, db: Session = Depends(get_db)) -> NewsResponse:
    news = news_service.get_news_by_id(db, news_id)
    if news is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found",
        )
    return news


@router.post("", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
def create_news(
    data: NewsCreate, db: Session = Depends(get_db)
) -> NewsResponse:
    return news_service.create_news(db, data)


@router.put("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: UUID, data: NewsUpdate, db: Session = Depends(get_db)
) -> NewsResponse:
    news = news_service.update_news(db, news_id, data)
    if news is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found",
        )
    return news


@router.patch("/{news_id}", response_model=NewsResponse)
def patch_news(
    news_id: UUID, data: NewsPatch, db: Session = Depends(get_db)
) -> NewsResponse:
    news = news_service.patch_news(db, news_id, data)
    if news is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found",
        )
    return news


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(news_id: UUID, db: Session = Depends(get_db)) -> None:
    deleted = news_service.delete_news(db, news_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found",
        )
