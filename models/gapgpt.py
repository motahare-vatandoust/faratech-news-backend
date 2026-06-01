from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(
        ...,
        min_length=1,
        description="Conversation messages (at least one user message)",
    )
    model: Optional[str] = Field(
        default=None,
        description="GapGPT model id (defaults to GAPGPT_DEFAULT_MODEL)",
    )


class ChatResponse(BaseModel):
    content: str
    model: str
