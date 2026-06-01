from typing import List, Optional

from openai import OpenAI

from core.config import GAPGPT_API_KEY, GAPGPT_BASE_URL, GAPGPT_DEFAULT_MODEL

_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    if not GAPGPT_API_KEY:
        raise ValueError(
            "GAPGPT_API_KEY is not set. Add it to your environment or .env file."
        )

    global _client
    if _client is None:
        _client = OpenAI(base_url=GAPGPT_BASE_URL, api_key=GAPGPT_API_KEY)
    return _client


def chat(
    messages: List[dict],
    *,
    model: Optional[str] = None,
) -> str:
    """Send a chat completion request to GapGPT and return the assistant text."""
    client = get_client()
    response = client.chat.completions.create(
        model=model or GAPGPT_DEFAULT_MODEL,
        messages=messages,
    )
    content = response.choices[0].message.content
    return content if content is not None else ""
