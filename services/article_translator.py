import json
import re
from dataclasses import dataclass
from typing import Optional

from core.config import GAPGPT_DEFAULT_MODEL, GAPGPT_TRANSLATION_MODEL
from services.gapgpt import chat

_SYSTEM_PROMPT = """You are a professional Persian (Farsi) editor and technical translator.

Given an English tech article (title, optional summary, and body), produce fluent, natural Farsi suitable for publication.

Rules:
- Translate accurately; preserve technical terms when commonly used in Farsi (or add brief clarification in parentheses).
- Clean the body: remove ads, navigation, duplicate headings, and broken fragments from web scraping.
- Use clear paragraphs; keep code blocks, URLs, and identifiers unchanged.
- Write right-to-left Persian with correct punctuation.
- Return ONLY valid JSON (no markdown fences) with exactly these keys:
  - "title": string
  - "summary": string or null
  - "content": string (full cleaned article body in Farsi)
"""


@dataclass
class TranslatedArticle:
    title: str
    content: str
    summary: Optional[str] = None


def _parse_translation_response(raw: str) -> TranslatedArticle:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    data = json.loads(text)
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    summary = data.get("summary")
    if summary is not None:
        summary = str(summary).strip() or None

    if not title or not content:
        raise ValueError("GapGPT response missing title or content")

    return TranslatedArticle(title=title, content=content, summary=summary)


def translate_article_to_farsi(
    *,
    title: str,
    content: str,
    summary: Optional[str] = None,
    model: Optional[str] = None,
) -> TranslatedArticle:
    """Translate and clean a crawled article into publication-ready Farsi."""
    payload = {
        "title": title,
        "summary": summary or "",
        "content": content,
    }
    raw = chat(
        [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False),
            },
        ],
        model=model or GAPGPT_TRANSLATION_MODEL or GAPGPT_DEFAULT_MODEL,
    )
    return _parse_translation_response(raw)
