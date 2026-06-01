from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, Protocol

import httpx

from crawler.config import (
    CRAWLER_IMPERSONATE,
    CRAWLER_MAX_RETRIES,
    CRAWLER_REQUEST_TIMEOUT,
    CRAWLER_USE_CURL_CFFI,
    CRAWLER_USER_AGENT,
)

_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

_CLOUDFLARE_MARKERS = (
    "cf-browser-verification",
    "challenge-platform",
    "Just a moment...",
    "Attention Required! | Cloudflare",
)


class HtmlFetcher(Protocol):
    async def get(self, url: str) -> str: ...


def default_headers() -> dict[str, str]:
    return {
        "User-Agent": CRAWLER_USER_AGENT or _DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }


def format_request_error(exc: BaseException, *, url: str = "") -> str:
    detail = str(exc).strip() or repr(exc)
    prefix = f"{url}: " if url else ""
    return f"{prefix}{type(exc).__name__}: {detail}"


def is_cloudflare_block(*, status_code: int, html: str) -> bool:
    if status_code == 403:
        return True
    lowered = html.lower()
    return any(marker.lower() in lowered for marker in _CLOUDFLARE_MARKERS)


class CloudflareBlockedError(PermissionError):
    """Raised when Cloudflare returns a block or challenge page."""


class _HttpxFetcher:
    def __init__(self) -> None:
        timeout = httpx.Timeout(
            CRAWLER_REQUEST_TIMEOUT, connect=CRAWLER_REQUEST_TIMEOUT
        )
        self._client = httpx.AsyncClient(
            headers=default_headers(),
            timeout=timeout,
            follow_redirects=True,
        )

    async def get(self, url: str) -> str:
        return await _fetch_with_retries(self._get_once, url)

    async def _get_once(self, url: str) -> str:
        response = await self._client.get(url)
        html = response.text
        if is_cloudflare_block(status_code=response.status_code, html=html):
            raise CloudflareBlockedError(
                f"HTTP {response.status_code} — Cloudflare blocked this request. "
                "Try a VPN, or set CRAWLER_USE_CURL_CFFI=true (default)."
            )
        response.raise_for_status()
        return html

    async def aclose(self) -> None:
        await self._client.aclose()


class _CurlCffiFetcher:
    def __init__(self) -> None:
        from curl_cffi.requests import AsyncSession

        self._session = AsyncSession(impersonate=CRAWLER_IMPERSONATE)

    async def get(self, url: str) -> str:
        return await _fetch_with_retries(self._get_once, url)

    async def _get_once(self, url: str) -> str:
        response = await self._session.get(
            url,
            timeout=CRAWLER_REQUEST_TIMEOUT,
        )
        html = response.text
        if is_cloudflare_block(status_code=response.status_code, html=html):
            raise CloudflareBlockedError(
                f"HTTP {response.status_code} — Cloudflare blocked this request. "
                "Use a VPN/proxy, or try another network."
            )
        if response.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {response.status_code}",
                request=None,
                response=None,
            )
        return html

    async def aclose(self) -> None:
        await self._session.close()


async def _fetch_with_retries(get_once, url: str) -> str:
    last_error: Optional[BaseException] = None
    for attempt in range(1, CRAWLER_MAX_RETRIES + 1):
        try:
            return await get_once(url)
        except Exception as exc:
            last_error = exc
            if attempt >= CRAWLER_MAX_RETRIES:
                raise last_error
    raise RuntimeError(f"Failed to fetch {url}")


def _create_fetcher() -> HtmlFetcher:
    if CRAWLER_USE_CURL_CFFI:
        try:
            return _CurlCffiFetcher()
        except ImportError:
            pass
    return _HttpxFetcher()


@asynccontextmanager
async def crawl_client() -> AsyncIterator[HtmlFetcher]:
    fetcher = _create_fetcher()
    try:
        yield fetcher
    finally:
        if hasattr(fetcher, "aclose"):
            await fetcher.aclose()


async def fetch_html(fetcher: HtmlFetcher, url: str) -> str:
    return await fetcher.get(url)
