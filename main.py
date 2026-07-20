import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import CORS_ORIGINS
from routers import admin_auth, crawler, gapgpt, health, news

_DEFAULT_CORS = []
if os.getenv("ENVIRONMENT", "development") != "production":
    _DEFAULT_CORS = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

app = FastAPI(
    title="Faratech News Backend",
    description="News API backend for Faratech",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_DEFAULT_CORS + CORS_ORIGINS,
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
