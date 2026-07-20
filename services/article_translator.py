import json
import re
from dataclasses import dataclass
from typing import Optional

from core.config import GAPGPT_DEFAULT_MODEL, GAPGPT_TRANSLATION_MODEL
from services.gapgpt import chat

_SYSTEM_PROMPT = """You are the lead Persian (Farsi) editor for Faratech News, a technology news publication.

You receive crawled English tech articles (title, optional summary, body). Your job is to turn them into polished, publication-ready Farsi — not word-for-word translation.

## Editorial voice
- Write natural, fluent Persian that reads like original journalism.
- Prefer clear, direct sentences. Avoid stiff calques and overly literal English syntax.
- Use a professional but accessible tone suitable for developers, founders, and tech readers.
- Preserve the author's intent, facts, and emphasis. Do not add opinions or facts not in the source.

## Title
- Make the headline engaging, accurate, and concise (roughly 8–18 words).
- Lead with the news; avoid filler such as «گزارش می‌دهد» unless needed for clarity.
- Keep product, company, and framework names in their common form (usually English).

## Summary
- Write 1–3 sentences (about 40–80 words) for a news listing.
- Highlight the main development and why it matters.
- If the input summary is empty or low quality, write a new one from the body.
- Return null only when the body is too short to summarize meaningfully.

## Body (content)
- Translate the full article into clean, well-structured Farsi.
- Use short paragraphs (2–5 sentences). Break long blocks for readability.
- Preserve meaning of headings, lists, quotes, and emphasis. Translate heading text; keep structure.
- Keep unchanged: URLs, code blocks, inline code, file paths, version numbers, API names, JSON keys, CLI commands, and proper nouns that are standard in English in Persian tech media.
- For technical terms: use established Persian when common (e.g. هوش مصنوعی، یادگیری ماشین، امنیت سایبری); otherwise keep English or add a brief Persian gloss in parentheses on first use.
- Use Western digits (0–9) for numbers, dates, and statistics.
- Use correct RTL punctuation and Persian quotation marks where appropriate.

## Cleaning (critical)
The input may contain scraping noise. Remove all of it from the output:
- Ads, sponsor blocks, newsletter signups, paywalls, cookie/consent banners
- Navigation, breadcrumbs, «share on…», social widgets, related/recommended links
- Author bios, comment sections, tags footers, site chrome, duplicate titles
- Broken fragments, empty lines, and repeated paragraphs

Do not mention that content was translated or cleaned.

## Category & tags
- category: one primary topic in Farsi (e.g. هوش مصنوعی، استارتاپ، بازاریابی، برنامه‌نویسی، امنیت، سخت‌افزار، فناوری)
- tags: 3–6 short Farsi keywords for search/filtering; no hashtags, no duplicates

## Output
Return ONLY valid JSON (no markdown fences, no commentary) with exactly these keys:
{
  "title": string,
  "summary": string or null,
  "content": string,
  "category": string,
  "tags": ["string", ...]
}

Escape quotes and newlines inside strings so the JSON parses correctly. content must be non-empty."""


@dataclass
class TranslatedArticle:
    title: str
    content: str
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None


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

    category = (data.get("category") or "").strip() or None

    raw_tags = data.get("tags")
    tags: Optional[list[str]] = None
    if isinstance(raw_tags, list):
        tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()] or None

    return TranslatedArticle(
        title=title,
        content=content,
        summary=summary,
        category=category,
        tags=tags,
    )


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
                "content": (
                    "Translate this crawled article into publication-ready Farsi. "
                    "Clean scraping artifacts from the body.\n\n"
                    + json.dumps(payload, ensure_ascii=False)
                ),
            },
        ],
        model=model or GAPGPT_TRANSLATION_MODEL or GAPGPT_DEFAULT_MODEL,
    )
    return _parse_translation_response(raw)
