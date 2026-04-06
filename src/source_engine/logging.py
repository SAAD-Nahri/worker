from __future__ import annotations

from collections import Counter
from typing import Iterable

from source_engine.models import FetchResult, SourceItem


def summarize_items(items: Iterable[SourceItem]) -> tuple[dict[str, int], dict[str, int]]:
    per_source = Counter()
    per_dedupe = Counter()
    for item in items:
        per_source[item.source_id] += 1
        per_dedupe[item.dedupe_status] += 1
    return dict(per_source), dict(per_dedupe)


def summarize_body_extraction(items: Iterable[SourceItem]) -> dict[str, int]:
    counts = Counter()
    for item in items:
        counts[item.body_extraction_status or "unknown"] += 1
    return dict(counts)


def print_run_summary(
    fetch_results: list[FetchResult],
    item_counts: dict[str, int],
    dedupe_counts: dict[str, int],
    body_extraction_counts: dict[str, int] | None = None,
) -> None:
    print("Source intake summary")
    print("====================")
    for result in fetch_results:
        status = result.status.upper()
        print(f"{result.source_id}: {status} feed_items={result.item_count} normalized_items={item_counts.get(result.source_id, 0)}")
        if result.error:
            print(f"  error: {result.error}")
        if result.fallback_action and result.fallback_action != "continue_normal":
            print(f"  fallback: {result.fallback_action}")
    print("Dedupe counts:")
    for key in sorted(dedupe_counts):
        print(f"  {key}: {dedupe_counts[key]}")
    if body_extraction_counts:
        print("Body extraction counts:")
        for key in sorted(body_extraction_counts):
            print(f"  {key}: {body_extraction_counts[key]}")
