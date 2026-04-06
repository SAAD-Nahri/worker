from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import uuid

from source_engine.models import SourceDecisionRecord, SourceRecord
from source_engine.source_status import (
    NON_INTAKE_STATUSES,
    VALID_SOURCE_STATUSES,
    SourceReviewSnapshot,
    recommend_source_status,
)
from source_engine.storage import DEFAULT_REGISTRY_PATH, SOURCE_DECISIONS_PATH, append_source_decisions, write_registry


def record_source_review_decision(
    source_id: str,
    reviewed_items: int,
    strong_candidates: int,
    weak_or_repetitive_items: int,
    fetch_failures: int = 0,
    reviewer_notes: str | None = None,
    final_status: str | None = None,
    apply_registry_update: bool = False,
    registry_path: Path | None = None,
    decision_path: Path | None = None,
) -> SourceDecisionRecord:
    active_registry_path = registry_path or DEFAULT_REGISTRY_PATH
    active_decision_path = decision_path or SOURCE_DECISIONS_PATH
    payload = _load_registry_payload(active_registry_path)
    source = _find_source_record(payload, source_id)

    snapshot = SourceReviewSnapshot(
        current_status=source.status,
        reviewed_items=reviewed_items,
        strong_candidates=strong_candidates,
        weak_or_repetitive_items=weak_or_repetitive_items,
        fetch_failures=fetch_failures,
    )
    recommendation = recommend_source_status(snapshot)
    resolved_final_status = final_status or recommendation.next_status
    if resolved_final_status not in VALID_SOURCE_STATUSES:
        raise ValueError(f"Invalid final source status: {resolved_final_status}")

    reviewed_at = datetime.now(UTC).isoformat()
    decision = SourceDecisionRecord(
        decision_id=_build_decision_id(source_id),
        source_id=source.source_id,
        source_name=source.source_name,
        reviewed_at=reviewed_at,
        current_status=source.status,
        recommended_status=recommendation.next_status,
        final_status=resolved_final_status,
        reviewed_items=reviewed_items,
        strong_candidates=strong_candidates,
        weak_or_repetitive_items=weak_or_repetitive_items,
        fetch_failures=fetch_failures,
        recommendation_reason=recommendation.reason,
        reviewer_notes=reviewer_notes,
        applied_to_registry=apply_registry_update,
    )
    append_source_decisions([decision], active_decision_path)

    if apply_registry_update:
        updated_payload = _apply_decision_to_payload(payload, decision)
        write_registry(active_registry_path, updated_payload)

    return decision


def _build_decision_id(source_id: str) -> str:
    return f"{source_id}-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"


def _load_registry_payload(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Source registry must be a list of source records.")
    return payload


def _find_source_record(payload: list[dict[str, object]], source_id: str) -> SourceRecord:
    for raw in payload:
        if raw.get("source_id") == source_id:
            return SourceRecord(**raw)
    raise ValueError(f"Unknown source_id: {source_id}")


def _apply_decision_to_payload(
    payload: list[dict[str, object]],
    decision: SourceDecisionRecord,
) -> list[dict[str, object]]:
    updated_payload: list[dict[str, object]] = []
    for raw in payload:
        if raw.get("source_id") != decision.source_id:
            updated_payload.append(raw)
            continue

        next_raw = dict(raw)
        next_raw["status"] = decision.final_status
        next_raw["active"] = decision.final_status not in NON_INTAKE_STATUSES
        next_raw["updated_at"] = decision.reviewed_at
        next_raw["last_reviewed_at"] = decision.reviewed_at
        next_raw["last_status_reason"] = decision.recommendation_reason
        next_raw["last_review_notes"] = decision.reviewer_notes
        if decision.final_status == "retired":
            next_raw["retirement_reason"] = decision.recommendation_reason
        elif "retirement_reason" in next_raw:
            next_raw["retirement_reason"] = None
        updated_payload.append(next_raw)
    return updated_payload
