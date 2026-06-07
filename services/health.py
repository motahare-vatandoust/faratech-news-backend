from sqlalchemy import text
from sqlalchemy.orm import Session

from models.health import HealthResponse


def get_health_status(db: Session) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        database = "error"

    return HealthResponse(status="ok", database=database)
