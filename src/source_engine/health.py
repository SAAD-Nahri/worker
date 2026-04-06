from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from source_engine.storage import (
    DEFAULT_REGISTRY_PATH,
    INTAKE_HISTORY_PATH,
    SOURCE_DECISIONS_PATH,
    SOURCE_ITEMS_PATH,
    read_jsonl_records,
)


@dataclass(frozen=True)
class SourceHealthRow:
    source_id: str
    source_name: str
    registry_status: str
    active: bool
    latest_fetch_status: str
    latest_processed_items: int
    latest_unique_items: int
    latest_duplicate_items: int
    latest_body_fetched: int
    latest_decision_status: str | None
    latest_decision_at: str | None
    latest_decision_reason: str | None
    latest_fallback_action: str | None
    review_signal: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "registry_status": self.registry_status,
            "active": self.active,
            "latest_fetch_status": self.latest_fetch_status,
            "latest_processed_items": self.latest_processed_items,
            "latest_unique_items": self.latest_unique_items,
            "latest_duplicate_items": self.latest_duplicate_items,
            "latest_body_fetched": self.latest_body_fetched,
            "latest_decision_status": self.latest_decision_status,
            "latest_decision_at": self.latest_decision_at,
            "latest_decision_reason": self.latest_decision_reason,
            "latest_fallback_action": self.latest_fallback_action,
            "review_signal": self.review_signal,
        }


def build_source_health_rows(
    registry_path: Path | None = None,
    intake_history_path: Path | None = None,
    source_items_path: Path | None = None,
    source_decisions_path: Path | None = None,
) -> tuple[str | None, list[SourceHealthRow]]:
    active_registry_path = registry_path or DEFAULT_REGISTRY_PATH
    active_intake_path = intake_history_path or INTAKE_HISTORY_PATH
    active_items_path = source_items_path or SOURCE_ITEMS_PATH
    active_decisions_path = source_decisions_path or SOURCE_DECISIONS_PATH

    registry_payload = _load_registry_payload(active_registry_path)
    latest_run = _latest_run_record(active_intake_path)
    latest_run_id = latest_run.get("run_id") if latest_run else None
    latest_items = _latest_run_items(active_items_path, latest_run_id)
    latest_decisions = _latest_decision_by_source(active_decisions_path)
    latest_fetch_by_source = {
        entry["source_id"]: entry for entry in latest_run.get("sources", [])
    } if latest_run else {}
    latest_item_metrics = _latest_item_metrics(latest_items)

    rows: list[SourceHealthRow] = []
    for raw in registry_payload:
        source_id = str(raw["source_id"])
        source_name = str(raw["source_name"])
        fetch_payload = latest_fetch_by_source.get(source_id, {})
        item_metrics = latest_item_metrics.get(
            source_id,
            {
                "processed": 0,
                "unique": 0,
                "duplicate": 0,
                "body_fetched": 0,
            },
        )
        decision = latest_decisions.get(source_id)
        rows.append(
            SourceHealthRow(
                source_id=source_id,
                source_name=source_name,
                registry_status=str(raw.get("status", "active")),
                active=bool(raw.get("active", False)),
                latest_fetch_status=str(fetch_payload.get("status", "no_run")),
                latest_processed_items=int(item_metrics["processed"]),
                latest_unique_items=int(item_metrics["unique"]),
                latest_duplicate_items=int(item_metrics["duplicate"]),
                latest_body_fetched=int(item_metrics["body_fetched"]),
                latest_decision_status=decision.get("final_status") if decision else None,
                latest_decision_at=decision.get("reviewed_at") if decision else None,
                latest_decision_reason=decision.get("recommendation_reason") if decision else None,
                latest_fallback_action=fetch_payload.get("fallback_action") if fetch_payload else None,
                review_signal=_review_signal(raw, decision, item_metrics, fetch_payload),
            )
        )
    return latest_run_id, rows


def _load_registry_payload(path: Path) -> list[dict[str, object]]:
    import json

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Source registry must be a list of source records.")
    return payload


def _latest_run_record(path: Path) -> dict[str, object] | None:
    records = read_jsonl_records(path)
    if not records:
        return None
    return records[-1]


def _latest_run_items(path: Path, run_id: str | None) -> list[dict[str, object]]:
    if not run_id:
        return []
    return [record for record in read_jsonl_records(path) if record.get("run_id") == run_id]


def _latest_decision_by_source(path: Path) -> dict[str, dict[str, object]]:
    decisions = read_jsonl_records(path)
    output: dict[str, dict[str, object]] = {}
    for decision in decisions:
        source_id = str(decision["source_id"])
        output[source_id] = decision
    return output


def _latest_item_metrics(items: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    metrics: dict[str, dict[str, int]] = {}
    for item in items:
        source_id = str(item["source_id"])
        bucket = metrics.setdefault(
            source_id,
            {"processed": 0, "unique": 0, "duplicate": 0, "body_fetched": 0},
        )
        bucket["processed"] += 1
        if item.get("dedupe_status") == "unique":
            bucket["unique"] += 1
        else:
            bucket["duplicate"] += 1
        if item.get("body_extraction_status") == "fetched":
            bucket["body_fetched"] += 1
    return metrics


def _review_signal(
    raw: dict[str, object],
    decision: dict[str, object] | None,
    item_metrics: dict[str, int],
    fetch_payload: dict[str, object],
) -> str:
    fetch_status = fetch_payload.get("status") if fetch_payload else None
    if fetch_status == "degraded":
        return "fallback_review_required"
    if fetch_status == "manual_only":
        return "manual_source_mode"
    if decision and decision.get("applied_to_registry") is False and decision.get("final_status") != raw.get("status"):
        return "decision_not_applied"
    if item_metrics["processed"] > 0 and item_metrics["unique"] == 0:
        return "review_needed_low_yield"
    if item_metrics["processed"] == 0:
        return "no_recent_items"
    if decision is None:
        return "review_pending"
    return "stable"
