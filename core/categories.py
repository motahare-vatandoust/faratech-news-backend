"""Canonical news categories shared by crawler, API, and clients."""

from __future__ import annotations

from typing import Optional

# Stable slugs stored in the DB and used by API filters / frontends.
NEWS_CATEGORY_SLUGS: tuple[str, ...] = (
    "ai",
    "programming",
    "marketing",
    "design",
    "startup",
    "cybersecurity",
    "hardware",
    "technology",
)

DEFAULT_CATEGORY = "technology"

CATEGORY_META: list[dict[str, object]] = [
    {
        "id": "ai",
        "label": {"en": "AI", "fa": "هوش مصنوعی"},
    },
    {
        "id": "programming",
        "label": {"en": "Programming", "fa": "برنامه‌نویسی"},
    },
    {
        "id": "marketing",
        "label": {"en": "Marketing", "fa": "بازاریابی"},
    },
    {
        "id": "design",
        "label": {"en": "Design", "fa": "طراحی"},
    },
    {
        "id": "startup",
        "label": {"en": "Startup", "fa": "استارتاپ"},
    },
    {
        "id": "cybersecurity",
        "label": {"en": "Security", "fa": "امنیت"},
    },
    {
        "id": "hardware",
        "label": {"en": "Hardware", "fa": "سخت‌افزار"},
    },
    {
        "id": "technology",
        "label": {"en": "Technology", "fa": "فناوری"},
    },
]

# Map free-form English / Farsi / legacy values → canonical slug.
_CATEGORY_ALIASES: dict[str, str] = {
    "ai": "ai",
    "artificial intelligence": "ai",
    "machine learning": "ai",
    "ml": "ai",
    "هوش مصنوعی": "ai",
    "یادگیری ماشین": "ai",
    "programming": "programming",
    "development": "programming",
    "software": "programming",
    "coding": "programming",
    "developer": "programming",
    "برنامه‌نویسی": "programming",
    "برنامه نویسی": "programming",
    "توسعه": "programming",
    "marketing": "marketing",
    "growth": "marketing",
    "بازاریابی": "marketing",
    "design": "design",
    "ux": "design",
    "ui": "design",
    "product design": "design",
    "طراحی": "design",
    "startup": "startup",
    "startups": "startup",
    "business": "startup",
    "استارتاپ": "startup",
    "cybersecurity": "cybersecurity",
    "security": "cybersecurity",
    "infosec": "cybersecurity",
    "امنیت": "cybersecurity",
    "امنیت سایبری": "cybersecurity",
    "hardware": "hardware",
    "gadgets": "hardware",
    "devices": "hardware",
    "سخت‌افزار": "hardware",
    "سخت افزار": "hardware",
    "technology": "technology",
    "tech": "technology",
    "general": "technology",
    "news": "technology",
    "فناوری": "technology",
    "عمومی": "technology",
}

# Title-case values previously written by crawler defaults.
_LEGACY_STORED: dict[str, tuple[str, ...]] = {
    "ai": ("AI",),
    "programming": ("Development",),
    "marketing": ("Marketing",),
    "design": ("Design",),
    "startup": ("Startup",),
    "cybersecurity": ("Security",),
    "hardware": ("Hardware",),
    "technology": ("General", "Technology"),
}


def is_valid_category(slug: str) -> bool:
    return slug in NEWS_CATEGORY_SLUGS


def normalize_category(value: Optional[str]) -> str:
    """Resolve any free-form category string to a canonical slug."""
    if not value:
        return DEFAULT_CATEGORY

    raw = value.strip()
    if not raw:
        return DEFAULT_CATEGORY

    lower = raw.lower()
    if lower in NEWS_CATEGORY_SLUGS:
        return lower

    if lower in _CATEGORY_ALIASES:
        return _CATEGORY_ALIASES[lower]

    if raw in _CATEGORY_ALIASES:
        return _CATEGORY_ALIASES[raw]

    for alias, slug in _CATEGORY_ALIASES.items():
        if alias in lower or alias in raw:
            return slug

    return DEFAULT_CATEGORY


def category_filter_values(slug: str) -> list[str]:
    """All DB values that should match a canonical category filter."""
    resolved = normalize_category(slug)
    values: list[str] = [resolved]
    values.extend(_LEGACY_STORED.get(resolved, ()))
    for alias, target in _CATEGORY_ALIASES.items():
        if target == resolved:
            values.append(alias)
    # Preserve order, drop dupes.
    return list(dict.fromkeys(values))


def list_categories() -> list[dict[str, object]]:
    return list(CATEGORY_META)
