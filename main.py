from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import crawler, gapgpt, health, news

app = FastAPI(
    title="Faratech News Backend",
    description="News API backend for Faratech",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(news.router)
app.include_router(crawler.router)
app.include_router(gapgpt.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
