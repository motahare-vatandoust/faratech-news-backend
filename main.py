from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import AUTO_CRAWLER_ENABLED, CORS_ORIGINS, CRAWLER_INTERVAL_MINUTES
from core.scheduler import (
    start_auto_crawler_scheduler,
    shutdown_auto_crawler_scheduler,
)
from routers import admin_auth, crawler, gapgpt, health, news

# Use uvicorn's logger so startup messages appear in server output.
logger = logging.getLogger("uvicorn.error")

# Local frontend ports — always allowed so `npm run dev` can hit the
# production API. Production site origins come from CORS_ORIGINS.
_LOCAL_CORS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
_allow_origins = list(dict.fromkeys(_LOCAL_CORS + CORS_ORIGINS))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting auto crawler scheduler (AUTO_CRAWLER_ENABLED=%s, CRAWLER_INTERVAL_MINUTES=%s)",
        AUTO_CRAWLER_ENABLED,
        CRAWLER_INTERVAL_MINUTES,
    )
    scheduler = start_auto_crawler_scheduler()
    if scheduler is not None and scheduler.running:
        logger.info(
            "Auto crawler scheduler is running (interval=%s minute(s), AUTO_CRAWLER_ENABLED=%s)",
            CRAWLER_INTERVAL_MINUTES,
            AUTO_CRAWLER_ENABLED,
        )
    else:
        logger.info(
            "Auto crawler scheduler is not running in this process "
            "(AUTO_CRAWLER_ENABLED=%s, interval=%s minute(s))",
            AUTO_CRAWLER_ENABLED,
            CRAWLER_INTERVAL_MINUTES,
        )
    try:
        yield
    finally:
        shutdown_auto_crawler_scheduler(scheduler)


app = FastAPI(
    title="Faratech News Backend",
    description="News API backend for Faratech",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(news.router)
app.include_router(crawler.router)
app.include_router(gapgpt.router)
app.include_router(admin_auth.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
