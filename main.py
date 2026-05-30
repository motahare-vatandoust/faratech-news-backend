from fastapi import FastAPI

from routers import health, news

app = FastAPI(
    title="Faratech News Backend",
    description="News API backend for Faratech",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(news.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
