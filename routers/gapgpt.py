from fastapi import APIRouter, HTTPException, status

from core.config import GAPGPT_DEFAULT_MODEL
from models.gapgpt import ChatRequest, ChatResponse
from services import gapgpt as gapgpt_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Chat completion via GapGPT (OpenAI-compatible API)."""
    try:
        content = gapgpt_service.chat(
            [message.model_dump() for message in request.messages],
            model=request.model,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"GapGPT request failed: {exc}",
        ) from exc

    return ChatResponse(
        content=content,
        model=request.model or GAPGPT_DEFAULT_MODEL,
    )
