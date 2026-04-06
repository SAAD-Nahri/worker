from __future__ import annotations

from datetime import UTC, datetime
import hashlib
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from source_engine.classify import classify_item
from source_engine.cleaner import clean_text, word_count
from source_engine.models import FetchEntry, SourceItem, SourceRecord


TRACKING_QUERY_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid"}


def normalize_source_item(source: SourceRecord, entry: FetchEntry, fetched_at: str) -> SourceItem:
    canonical_url = normalize_url(entry.link)
    raw_title = clean_text(entry.title)
    raw_summary = clean_text(entry.summary)
    raw_body_text = clean_text(entry.content or entry.summary)
    published_at = entry.published_at

    quality_flags: list[str] = []
    if not raw_title:
        quality_flags.append("missing_title")
    if not canonical_url:
        quality_flags.append("missing_url")
    if not raw_summary:
        quality_flags.append("missing_summary")
    if source.body_extraction_required:
        quality_flags.append("article_body_not_fetched")

    freshness_label = classify_freshness(published_at, fetched_at)
    item_id = build_item_id(source.source_id, canonical_url, raw_title)

    item = SourceItem(
        item_id=item_id,
        source_id=source.source_id,
        source_name=source.source_name,
        source_family=source.source_family,
        run_id=None,
        source_url=entry.link,
        canonical_url=canonical_url,
        discovered_at=fetched_at,
        fetched_at=fetched_at,
        raw_title=raw_title,
        raw_summary=raw_summary,
        raw_body_text=raw_body_text,
        author_name=entry.author_name,
        published_at=published_at,
        topical_label="unclassified",
        freshness_label=freshness_label,
        normalization_status="normalized",
        dedupe_status="pending",
        body_extraction_status="pending" if source.body_extraction_required else "not_required",
        body_word_count=word_count(raw_body_text),
        quality_flags=quality_flags,
        normalized_title=normalize_title_for_storage(raw_title),
        content_hash=hashlib.sha1(raw_body_text.encode("utf-8")).hexdigest() if raw_body_text else None,
    )
    template_suggestion, topical_label = classify_item(item)
    item.template_suggestion = template_suggestion
    item.topical_label = topical_label
    return item


def normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url.strip())
    filtered_query = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if key not in TRACKING_QUERY_PARAMS]
    normalized_query = urlencode(filtered_query)
    clean_path = parsed.path.rstrip("/") or parsed.path
    return urlunparse((parsed.scheme, parsed.netloc.lower(), clean_path, "", normalized_query, ""))


def classify_freshness(published_at: str | None, fetched_at: str) -> str:
    if not published_at:
        return "unknown"

    published_dt = _try_parse_datetime(published_at)
    fetched_dt = _try_parse_datetime(fetched_at)
    if published_dt is None or fetched_dt is None:
        return "unknown"

    delta_days = (fetched_dt - published_dt).days
    if delta_days <= 7:
        return "fresh"
    if delta_days <= 30:
        return "recent"
    return "evergreen"


def build_item_id(source_id: str, canonical_url: str, raw_title: str) -> str:
    seed = f"{source_id}|{canonical_url}|{raw_title}".encode("utf-8")
    return hashlib.sha1(seed).hexdigest()


def normalize_title_for_storage(title: str) -> str:
    return " ".join(clean_text(title).lower().split())


def _try_parse_datetime(value: str) -> datetime | None:
    candidates = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    fixed = value.replace("Z", "+00:00")
    for candidate in candidates:
        try:
            parsed = datetime.strptime(fixed, candidate)
            return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            continue
    return None
