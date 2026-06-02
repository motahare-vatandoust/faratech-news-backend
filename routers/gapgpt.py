from fastapi import APIRouter, HTTPException, status
from openai import APIConnectionError, AuthenticationError, PermissionDeniedError, RateLimitError

from core.config import GAPGPT_DEFAULT_MODEL
from models.gapgpt import ChatRequest, ChatResponse
from services import gapgpt as gapgpt_service

router = APIRouter(prefix="/ai", tags=["ai"])


def _gapgpt_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ValueError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GAPGPT_API_KEY is not set. Add it to your .env file.",
        )

    if isinstance(exc, AuthenticationError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Invalid GAPGPT_API_KEY. Check your .env file.",
        )

    if isinstance(exc, PermissionDeniedError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GapGPT quota exhausted or access denied. Top up your account or use a new API key.",
        )

    if isinstance(exc, RateLimitError):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="GapGPT rate limit reached. Try again in a moment.",
        )

    if isinstance(exc, APIConnectionError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not connect to GapGPT. Check your network or GAPGPT_BASE_URL.",
        )

    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"GapGPT request failed: {exc}",
    )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Chat completion via GapGPT (OpenAI-compatible API)."""
    try:
        content = gapgpt_service.chat(
            [message.model_dump() for message in request.messages],
            model=request.model,
        )
    except Exception as exc:
        raise _gapgpt_http_error(exc) from exc

    return ChatResponse(
        content=content,
        model=request.model or GAPGPT_DEFAULT_MODEL,
    )
