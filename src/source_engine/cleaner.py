from __future__ import annotations

import html
import re


TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def clean_text(value: str | None) -> str:
    """Strip HTML and normalize whitespace."""
    if not value:
        return ""
    unescaped = html.unescape(value)
    without_tags = TAG_RE.sub(" ", unescaped)
    return WHITESPACE_RE.sub(" ", without_tags).strip()


def word_count(value: str | None) -> int:
    return len(clean_text(value).split())
