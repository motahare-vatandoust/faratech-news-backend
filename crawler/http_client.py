from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx

from crawler.config import CRAWLER_REQUEST_TIMEOUT, CRAWLER_USER_AGENT


def default_headers() -> dict[str, str]:
    return {
        "User-Agent": CRAWLER_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }


@asynccontextmanager
async def crawl_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        headers=default_headers(),
        timeout=CRAWLER_REQUEST_TIMEOUT,
        follow_redirects=True,
    ) as client:
        yield client


async def fetch_html(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url)
    response.raise_for_status()
    return response.text
