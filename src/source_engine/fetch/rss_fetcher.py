from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterable
from urllib.request import urlopen
import xml.etree.ElementTree as ET

from source_engine.cleaner import clean_text
from source_engine.fetch.http import build_request, read_response_payload
from source_engine.models import FetchEntry, FetchResult, SourceRecord


ATOM_NS = "{http://www.w3.org/2005/Atom}"
CONTENT_NS = "{http://purl.org/rss/1.0/modules/content/}"
DC_NS = "{http://purl.org/dc/elements/1.1/}"
RSS_SOURCE_TYPES = {"rss_native", "rss_plus_fetch"}


def fetch_feed_entries(source: SourceRecord, timeout: int = 20) -> tuple[FetchResult, list[FetchEntry]]:
    fetched_at = datetime.now(UTC).isoformat()
    if source.source_type == "manual_seed":
        return (
            FetchResult(
                source_id=source.source_id,
                source_name=source.source_name,
                feed_url=source.rss_feed_url,
                fetched_at=fetched_at,
                status="manual_only",
                item_count=0,
                error="Manual-seed sources are not auto-fetched in Phase 1.",
                fallback_action="manual_seed_review",
            ),
            [],
        )
    if source.source_type == "selective_scrape":
        return (
            FetchResult(
                source_id=source.source_id,
                source_name=source.source_name,
                feed_url=source.rss_feed_url,
                fetched_at=fetched_at,
                status="manual_only",
                item_count=0,
                error="Selective-scrape sources remain manual review inputs in Phase 1.",
                fallback_action="manual_selective_scrape_review",
            ),
            [],
        )
    if source.source_type not in RSS_SOURCE_TYPES:
        return (
            FetchResult(
                source_id=source.source_id,
                source_name=source.source_name,
                feed_url=source.rss_feed_url,
                fetched_at=fetched_at,
                status="manual_only",
                item_count=0,
                error=f"Unsupported source_type for Phase 1 auto intake: {source.source_type}",
                fallback_action="manual_source_review",
            ),
            [],
        )
    if not source.rss_feed_url:
        return (
            FetchResult(
                source_id=source.source_id,
                source_name=source.source_name,
                feed_url=source.rss_feed_url,
                fetched_at=fetched_at,
                status="degraded",
                item_count=0,
                error="RSS-first source has no feed configured.",
                fallback_action="manual_source_review",
            ),
            [],
        )

    request = build_request(source.rss_feed_url)
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = read_response_payload(response)
    except Exception as exc:  # pragma: no cover - network failure branch
        return (
            FetchResult(
                source_id=source.source_id,
                source_name=source.source_name,
                feed_url=source.rss_feed_url,
                fetched_at=fetched_at,
                status="degraded",
                item_count=0,
                error=f"Feed fetch failure: {exc}",
                fallback_action="manual_source_review",
            ),
            [],
        )

    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        return (
            FetchResult(
                source_id=source.source_id,
                source_name=source.source_name,
                feed_url=source.rss_feed_url,
                fetched_at=fetched_at,
                status="degraded",
                item_count=0,
                error=f"XML parse failure: {exc}",
                fallback_action="manual_source_review",
            ),
            [],
        )

    if root.tag.lower().endswith("rss"):
        entries = list(_parse_rss(root))
    elif root.tag.lower().endswith("feed"):
        entries = list(_parse_atom(root))
    else:
        return (
            FetchResult(
                source_id=source.source_id,
                source_name=source.source_name,
                feed_url=source.rss_feed_url,
                fetched_at=fetched_at,
                status="degraded",
                item_count=0,
                error=f"Unsupported feed root tag: {root.tag}",
                fallback_action="manual_source_review",
            ),
            [],
        )
    return (
        FetchResult(
            source_id=source.source_id,
            source_name=source.source_name,
            feed_url=source.rss_feed_url,
            fetched_at=fetched_at,
            status="ok",
            item_count=len(entries),
            fallback_action="continue_normal",
        ),
        entries,
    )


def _parse_rss(root: ET.Element) -> Iterable[FetchEntry]:
    channel = root.find("channel")
    if channel is None:
        return []
    items = channel.findall("item")
    return [_entry_from_rss_item(item) for item in items]


def _entry_from_rss_item(item: ET.Element) -> FetchEntry:
    title = clean_text(_child_text(item, "title"))
    link = clean_text(_child_text(item, "link"))
    summary = clean_text(_child_text(item, "description"))
    content = clean_text(_child_text(item, f"{CONTENT_NS}encoded"))
    author_name = clean_text(_child_text(item, "author") or _child_text(item, f"{DC_NS}creator")) or None
    published_at = clean_text(_child_text(item, "pubDate")) or None
    return FetchEntry(
        title=title,
        link=link,
        summary=summary,
        content=content,
        author_name=author_name,
        published_at=published_at,
    )


def _parse_atom(root: ET.Element) -> Iterable[FetchEntry]:
    entries = root.findall(f"{ATOM_NS}entry")
    return [_entry_from_atom_entry(entry) for entry in entries]


def _entry_from_atom_entry(entry: ET.Element) -> FetchEntry:
    title = clean_text(_child_text(entry, f"{ATOM_NS}title"))
    link = ""
    for candidate in entry.findall(f"{ATOM_NS}link"):
        href = candidate.attrib.get("href", "")
        rel = candidate.attrib.get("rel", "alternate")
        if href and rel == "alternate":
            link = href
            break
    summary = clean_text(_child_text(entry, f"{ATOM_NS}summary"))
    content = clean_text(_child_text(entry, f"{ATOM_NS}content"))
    author_name = clean_text(_child_text(entry, f"{ATOM_NS}author/{ATOM_NS}name")) or None
    published_at = clean_text(
        _child_text(entry, f"{ATOM_NS}published") or _child_text(entry, f"{ATOM_NS}updated")
    ) or None
    return FetchEntry(
        title=title,
        link=link,
        summary=summary,
        content=content,
        author_name=author_name,
        published_at=published_at,
    )


def _child_text(element: ET.Element, path: str) -> str:
    node = element.find(path)
    if node is None or node.text is None:
        return ""
    return node.text
