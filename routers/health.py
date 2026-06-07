from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from models.health import HealthResponse
from services.health import get_health_status

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    return get_health_status(db)
