from __future__ import annotations

import hashlib
import re
from urllib.request import urlopen

from source_engine.cleaner import clean_text, word_count
from source_engine.fetch.http import build_request, decode_response_text, read_response_payload, url_matches_domain
from source_engine.models import ArticleBodyResult, SourceItem, SourceRecord


ARTICLE_TAG_RE = re.compile(r"<article\b[^>]*>(.*?)</article>", re.IGNORECASE | re.DOTALL)
MAIN_TAG_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.IGNORECASE | re.DOTALL)
BODY_TAG_RE = re.compile(r"<body\b[^>]*>(.*?)</body>", re.IGNORECASE | re.DOTALL)
SCRIPT_STYLE_RE = re.compile(
    r"<(script|style|noscript|svg|iframe)[^>]*>.*?</\1>",
    re.IGNORECASE | re.DOTALL,
)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
TEXT_BLOCK_RE = re.compile(r"<(?:p|h2|h3|li)[^>]*>(.*?)</(?:p|h2|h3|li)>", re.IGNORECASE | re.DOTALL)
COMMENT_AUTHOR_RE = re.compile(r"^[a-z0-9 .,'-]{1,40}\s+says:", re.IGNORECASE)
BOILERPLATE_MARKERS = {
    "newsletter",
    "subscribe",
    "advertisement",
    "all rights reserved",
    "cookie policy",
    "privacy policy",
    "your email address will not be published",
    "this site uses akismet",
    "toggle child menu",
    "recipe index",
    "meet our cultural experts",
    "cooking and baking conversions",
    "where will you travel today",
}
QUALITY_FLAG_BY_STATUS = {
    "blocked_external_domain": "article_fetch_blocked",
    "unsupported_content_type": "article_fetch_unsupported",
    "fetch_error": "article_fetch_failed",
    "extraction_weak": "article_body_weak_extraction",
    "missing_url": "article_fetch_missing_url",
}
MIN_ARTICLE_WORDS = 80


def should_fetch_article_body(source: SourceRecord, item: SourceItem, enabled: bool) -> bool:
    return (
        enabled
        and source.body_extraction_required
        and item.dedupe_status == "unique"
        and bool(item.canonical_url)
    )


def fetch_article_body(source: SourceRecord, url: str, timeout: int = 20) -> ArticleBodyResult:
    if not url:
        return ArticleBodyResult(url=url, status="missing_url", body_text="", word_count=0, error="Missing URL.")
    if not url_matches_domain(url, source.domain):
        return ArticleBodyResult(
            url=url,
            status="blocked_external_domain",
            body_text="",
            word_count=0,
            error=f"URL hostname is outside allowed domain {source.domain}.",
        )

    request = build_request(url)
    try:
        with urlopen(request, timeout=timeout) as response:
            content_type = response.getheader("Content-Type") or ""
            if "html" not in content_type.lower():
                return ArticleBodyResult(
                    url=url,
                    status="unsupported_content_type",
                    body_text="",
                    word_count=0,
                    error=f"Unsupported content type: {content_type or 'unknown'}",
                )
            payload = read_response_payload(response)
    except Exception as exc:  # pragma: no cover - network failure branch
        return ArticleBodyResult(url=url, status="fetch_error", body_text="", word_count=0, error=str(exc))

    html_text = decode_response_text(payload, content_type)
    article_text = extract_article_text(html_text)
    extracted_word_count = word_count(article_text)
    if extracted_word_count < MIN_ARTICLE_WORDS:
        return ArticleBodyResult(
            url=url,
            status="extraction_weak",
            body_text=article_text,
            word_count=extracted_word_count,
            error=f"Extracted body too weak: {extracted_word_count} words.",
        )

    return ArticleBodyResult(
        url=url,
        status="fetched",
        body_text=article_text,
        word_count=extracted_word_count,
    )


def apply_article_body_result(item: SourceItem, result: ArticleBodyResult) -> None:
    item.body_extraction_status = result.status
    item.body_word_count = result.word_count or word_count(item.raw_body_text)
    if result.status == "fetched":
        item.raw_body_text = result.body_text
        item.content_hash = hashlib.sha1(result.body_text.encode("utf-8")).hexdigest()
        item.quality_flags = [flag for flag in item.quality_flags if flag != "article_body_not_fetched"]
        return

    quality_flag = QUALITY_FLAG_BY_STATUS.get(result.status)
    if quality_flag and quality_flag not in item.quality_flags:
        item.quality_flags.append(quality_flag)


def extract_article_text(html_text: str) -> str:
    if not html_text:
        return ""

    cleaned_html = SCRIPT_STYLE_RE.sub(" ", html_text)
    cleaned_html = COMMENT_RE.sub(" ", cleaned_html)
    content_region = _select_content_region(cleaned_html)

    blocks: list[str] = []
    for match in TEXT_BLOCK_RE.finditer(content_region):
        candidate = clean_text(match.group(1))
        if _is_candidate_text_block(candidate):
            blocks.append(candidate)

    deduped_blocks = _dedupe_preserving_order(blocks)
    return "\n\n".join(deduped_blocks)


def _select_content_region(html_text: str) -> str:
    candidates = []
    for pattern in (ARTICLE_TAG_RE, MAIN_TAG_RE, BODY_TAG_RE):
        candidates.extend(match.group(1) for match in pattern.finditer(html_text))
    if not candidates:
        return html_text
    return max(candidates, key=len)


def _is_candidate_text_block(value: str) -> bool:
    if word_count(value) < 8:
        return False
    lowered = value.lower()
    if COMMENT_AUTHOR_RE.match(lowered):
        return False
    return not any(marker in lowered for marker in BOILERPLATE_MARKERS)


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output
