from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from content_engine.storage import DRAFT_RECORDS_PATH, read_draft_records
from media_engine.storage import ASSET_RECORDS_PATH
from distribution_engine.health import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    SOCIAL_PACKAGE_REVIEWS_PATH,
    DistributionHealthRow,
    build_distribution_health_report,
)
from tracking_engine.audit import build_tracking_audit_report
from tracking_engine.storage import TRACKING_AUDIT_RECORDS_PATH


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"
DEFAULT_WORDPRESS_CONFIG_PATH = CONFIG_DIR / "wordpress_rest_config.local.json"
DEFAULT_FACEBOOK_CONFIG_PATH = CONFIG_DIR / "facebook_graph_config.local.json"


@dataclass(frozen=True)
class ActivationConfigStatus:
    config_name: str
    config_path: str
    exists: bool
    parse_valid: bool
    ready_for_execute: bool
    placeholder_detected: bool
    missing_fields: tuple[str, ...] = ()
    masked_target: str | None = None
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "config_name": self.config_name,
            "config_path": self.config_path,
            "exists": self.exists,
            "parse_valid": self.parse_valid,
            "ready_for_execute": self.ready_for_execute,
            "placeholder_detected": self.placeholder_detected,
            "missing_fields": list(self.missing_fields),
            "masked_target": self.masked_target,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class ActivationDraftCandidateRow:
    draft_id: str
    source_item_id: str
    source_id: str
    source_domain: str
    template_id: str
    category: str
    headline_selected: str
    approval_state: str
    workflow_state: str
    quality_gate_status: str
    derivative_risk_level: str
    updated_at: str

    def to_dict(self) -> dict[str, object]:
        return {
            "draft_id": self.draft_id,
            "source_item_id": self.source_item_id,
            "source_id": self.source_id,
            "source_domain": self.source_domain,
            "template_id": self.template_id,
            "category": self.category,
            "headline_selected": self.headline_selected,
            "approval_state": self.approval_state,
            "workflow_state": self.workflow_state,
            "quality_gate_status": self.quality_gate_status,
            "derivative_risk_level": self.derivative_risk_level,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True)
class SystemActivationSummary:
    readiness_signal: str
    blocking_reasons: tuple[str, ...]
    latest_distribution_snapshot_at: str | None
    latest_transport_validation_at: str | None
    wordpress_config_ready: bool
    facebook_config_ready: bool
    approved_pass_draft_count: int
    local_canary_chain_count: int
    successful_wordpress_validations: int
    successful_facebook_validations: int
    next_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "readiness_signal": self.readiness_signal,
            "blocking_reasons": list(self.blocking_reasons),
            "latest_distribution_snapshot_at": self.latest_distribution_snapshot_at,
            "latest_transport_validation_at": self.latest_transport_validation_at,
            "wordpress_config_ready": self.wordpress_config_ready,
            "facebook_config_ready": self.facebook_config_ready,
            "approved_pass_draft_count": self.approved_pass_draft_count,
            "local_canary_chain_count": self.local_canary_chain_count,
            "successful_wordpress_validations": self.successful_wordpress_validations,
            "successful_facebook_validations": self.successful_facebook_validations,
            "next_steps": list(self.next_steps),
        }


def build_system_activation_readiness_report(
    *,
    wordpress_config_path: Path | None = None,
    facebook_config_path: Path | None = None,
    draft_records_path: Path | None = None,
    blog_publish_records_path: Path | None = None,
    social_package_records_path: Path | None = None,
    social_package_reviews_path: Path | None = None,
    asset_records_path: Path | None = None,
    facebook_publish_records_path: Path | None = None,
    queue_item_records_path: Path | None = None,
    mapping_records_path: Path | None = None,
    audit_records_path: Path | None = None,
) -> tuple[SystemActivationSummary, list[ActivationConfigStatus], list[ActivationDraftCandidateRow], list[DistributionHealthRow]]:
    wordpress_status = _inspect_wordpress_config(wordpress_config_path or DEFAULT_WORDPRESS_CONFIG_PATH)
    facebook_status = _inspect_facebook_config(facebook_config_path or DEFAULT_FACEBOOK_CONFIG_PATH)
    config_statuses = [wordpress_status, facebook_status]

    candidate_rows = _build_activation_candidates(draft_records_path or DRAFT_RECORDS_PATH)
    _, canary_rows = build_distribution_health_report(
        blog_publish_records_path=blog_publish_records_path or BLOG_PUBLISH_RECORDS_PATH,
        social_package_records_path=social_package_records_path or SOCIAL_PACKAGE_RECORDS_PATH,
        social_package_reviews_path=social_package_reviews_path or SOCIAL_PACKAGE_REVIEWS_PATH,
        asset_records_path=asset_records_path or ASSET_RECORDS_PATH,
        facebook_publish_records_path=facebook_publish_records_path or FACEBOOK_PUBLISH_RECORDS_PATH,
        queue_item_records_path=queue_item_records_path or QUEUE_ITEM_RECORDS_PATH,
        mapping_records_path=mapping_records_path or BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    )
    audit_summary, audit_records = build_tracking_audit_report(
        audit_records_path or TRACKING_AUDIT_RECORDS_PATH
    )

    successful_wordpress_validations, latest_wordpress_validation_at = _successful_transport_validation_stats(
        audit_records,
        entity_type="wordpress_transport",
    )
    successful_facebook_validations, latest_facebook_validation_at = _successful_transport_validation_stats(
        audit_records,
        entity_type="facebook_transport",
    )
    latest_transport_validation_at = _latest_non_empty(
        latest_wordpress_validation_at,
        latest_facebook_validation_at,
    )

    blocking_reasons = _resolve_blocking_reasons(
        wordpress_status=wordpress_status,
        facebook_status=facebook_status,
        approved_candidate_count=len(candidate_rows),
        local_canary_chain_count=len(canary_rows),
        successful_wordpress_validations=successful_wordpress_validations,
        successful_facebook_validations=successful_facebook_validations,
        canary_rows=canary_rows,
    )
    summary = SystemActivationSummary(
        readiness_signal=_resolve_readiness_signal(blocking_reasons),
        blocking_reasons=blocking_reasons,
        latest_distribution_snapshot_at=max((row.latest_updated_at for row in canary_rows), default=None),
        latest_transport_validation_at=latest_transport_validation_at or audit_summary.latest_event_at,
        wordpress_config_ready=wordpress_status.ready_for_execute,
        facebook_config_ready=facebook_status.ready_for_execute,
        approved_pass_draft_count=len(candidate_rows),
        local_canary_chain_count=len(canary_rows),
        successful_wordpress_validations=successful_wordpress_validations,
        successful_facebook_validations=successful_facebook_validations,
        next_steps=_resolve_next_steps(blocking_reasons),
    )
    return summary, config_statuses, candidate_rows, canary_rows


def _build_activation_candidates(draft_records_path: Path) -> list[ActivationDraftCandidateRow]:
    latest_by_id = {}
    for record in read_draft_records(draft_records_path):
        latest_by_id[record.draft_id] = record

    rows: list[ActivationDraftCandidateRow] = []
    for record in latest_by_id.values():
        if record.approval_state != "approved" or record.quality_gate_status != "pass":
            continue
        rows.append(
            ActivationDraftCandidateRow(
                draft_id=record.draft_id,
                source_item_id=record.source_item_id,
                source_id=record.source_id,
                source_domain=record.source_domain,
                template_id=record.template_id,
                category=record.category,
                headline_selected=record.headline_selected,
                approval_state=record.approval_state,
                workflow_state=record.workflow_state,
                quality_gate_status=record.quality_gate_status,
                derivative_risk_level=record.derivative_risk_level,
                updated_at=record.updated_at,
            )
        )
    rows.sort(key=lambda row: (row.updated_at, row.draft_id), reverse=True)
    return rows


def _inspect_wordpress_config(path: Path) -> ActivationConfigStatus:
    exists, payload, parse_valid, missing_fields = _load_json_config(path)
    notes: list[str] = []
    placeholder_detected = False
    masked_target = None
    if parse_valid and isinstance(payload, dict):
        base_url = str(payload.get("base_url", "")).strip()
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("application_password", "")).strip()
        masked_target = base_url or None
        if base_url == "https://example.com":
            placeholder_detected = True
            notes.append("base_url_placeholder")
        if username == "wordpress_username":
            placeholder_detected = True
            notes.append("username_placeholder")
        if not password or "xxxx" in password.lower():
            placeholder_detected = True
            notes.append("application_password_placeholder")
        if not isinstance(payload.get("category_id_by_name"), dict) or not payload.get("category_id_by_name"):
            notes.append("category_mapping_missing_or_empty")
        if not isinstance(payload.get("tag_id_by_name"), dict):
            notes.append("tag_mapping_not_object")
    return ActivationConfigStatus(
        config_name="wordpress",
        config_path=str(path),
        exists=exists,
        parse_valid=parse_valid,
        ready_for_execute=exists and parse_valid and not placeholder_detected and not missing_fields,
        placeholder_detected=placeholder_detected,
        missing_fields=tuple(missing_fields),
        masked_target=masked_target,
        notes=tuple(notes),
    )


def _inspect_facebook_config(path: Path) -> ActivationConfigStatus:
    exists, payload, parse_valid, missing_fields = _load_json_config(path)
    notes: list[str] = []
    placeholder_detected = False
    masked_target = None
    if parse_valid and isinstance(payload, dict):
        page_id = str(payload.get("page_id", "")).strip()
        token = str(payload.get("page_access_token", "")).strip()
        masked_target = _mask_value(page_id)
        if page_id == "123456789012345":
            placeholder_detected = True
            notes.append("page_id_placeholder")
        if not token or "placeholder" in token.lower() or "replace_locally" in token.lower():
            placeholder_detected = True
            notes.append("page_access_token_placeholder")
    return ActivationConfigStatus(
        config_name="facebook",
        config_path=str(path),
        exists=exists,
        parse_valid=parse_valid,
        ready_for_execute=exists and parse_valid and not placeholder_detected and not missing_fields,
        placeholder_detected=placeholder_detected,
        missing_fields=tuple(missing_fields),
        masked_target=masked_target,
        notes=tuple(notes),
    )


def _load_json_config(path: Path) -> tuple[bool, dict[str, object] | None, bool, list[str]]:
    if not path.exists():
        return False, None, False, ["file_missing"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return True, None, False, ["invalid_json"]
    if not isinstance(payload, dict):
        return True, None, False, ["root_not_object"]
    missing_fields = [
        field_name
        for field_name in _required_field_names(path.name)
        if not str(payload.get(field_name, "")).strip()
    ]
    return True, payload, True, missing_fields


def _required_field_names(filename: str) -> tuple[str, ...]:
    if "wordpress" in filename:
        return ("base_url", "username", "application_password")
    if "facebook" in filename:
        return ("page_id", "page_access_token")
    return ()


def _successful_transport_validation_stats(records, *, entity_type: str) -> tuple[int, str | None]:
    matched = [
        record
        for record in records
        if record.event_type == "transport_validation"
        and record.entity_type == entity_type
        and record.event_status == "success"
        and record.execution_mode == "execute"
    ]
    return len(matched), max((record.event_timestamp for record in matched), default=None)


def _resolve_blocking_reasons(
    *,
    wordpress_status: ActivationConfigStatus,
    facebook_status: ActivationConfigStatus,
    approved_candidate_count: int,
    local_canary_chain_count: int,
    successful_wordpress_validations: int,
    successful_facebook_validations: int,
    canary_rows: list[DistributionHealthRow],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not wordpress_status.exists:
        reasons.append("wordpress_config_missing")
    elif not wordpress_status.ready_for_execute:
        reasons.append("wordpress_config_not_ready")
    if not facebook_status.exists:
        reasons.append("facebook_config_missing")
    elif not facebook_status.ready_for_execute:
        reasons.append("facebook_config_not_ready")
    if approved_candidate_count == 0:
        reasons.append("approved_pass_draft_missing")
    if local_canary_chain_count == 0:
        reasons.append("local_canary_chain_missing")
    if successful_wordpress_validations == 0:
        reasons.append("wordpress_execute_validation_missing")
    if successful_facebook_validations == 0:
        reasons.append("facebook_execute_validation_missing")
    if _has_failed_live_canary_chain(canary_rows):
        reasons.append("live_canary_retry_required")
    elif canary_rows and not _has_live_canary_chain(canary_rows):
        reasons.append("live_canary_execution_missing")
    return tuple(reasons)


def _has_live_canary_chain(rows: list[DistributionHealthRow]) -> bool:
    for row in rows:
        if row.has_remote_wordpress_post and (
            row.facebook_publish_status in {"scheduled", "published"} or row.has_facebook_post_id
        ):
            return True
    return False


def _has_failed_live_canary_chain(rows: list[DistributionHealthRow]) -> bool:
    for row in rows:
        if row.facebook_publish_status == "failed":
            return True
    return False


def _resolve_readiness_signal(blocking_reasons: tuple[str, ...]) -> str:
    blocking_set = set(blocking_reasons)
    if not blocking_set:
        return "ready_for_phase_4_5_closeout"
    if "wordpress_config_missing" in blocking_set or "facebook_config_missing" in blocking_set:
        return "config_scaffolding_missing"
    if "wordpress_config_not_ready" in blocking_set or "facebook_config_not_ready" in blocking_set:
        return "awaiting_real_credentials"
    if "approved_pass_draft_missing" in blocking_set:
        return "awaiting_approved_canary_draft"
    if "local_canary_chain_missing" in blocking_set:
        return "awaiting_local_canary_chain"
    if "wordpress_execute_validation_missing" in blocking_set or "facebook_execute_validation_missing" in blocking_set:
        return "awaiting_execute_validation"
    if "live_canary_retry_required" in blocking_set:
        return "canary_retry_required"
    if "live_canary_execution_missing" in blocking_set:
        return "awaiting_live_canary_execution"
    return "activation_blocked"


def _resolve_next_steps(blocking_reasons: tuple[str, ...]) -> tuple[str, ...]:
    blocking_set = set(blocking_reasons)
    steps: list[str] = []
    if "wordpress_config_missing" in blocking_set or "facebook_config_missing" in blocking_set:
        steps.append("Create the ignored local WordPress and Facebook config files from the example configs.")
    if "wordpress_config_not_ready" in blocking_set:
        steps.append("Replace the placeholder WordPress base URL, username, and application password with real operator values.")
    if "facebook_config_not_ready" in blocking_set:
        steps.append("Replace the placeholder Facebook Page id and Page access token with real operator values.")
    if "approved_pass_draft_missing" in blocking_set:
        steps.append("Approve one low-risk pass-quality draft for the activation canary.")
    if "local_canary_chain_missing" in blocking_set:
        steps.append("Run the local canary-preparation chain through WordPress preparation, social packaging, and linkage.")
    if "wordpress_execute_validation_missing" in blocking_set:
        steps.append("Run execute-mode WordPress transport validation with audit recording.")
    if "facebook_execute_validation_missing" in blocking_set:
        steps.append("Run execute-mode Facebook transport validation with audit recording.")
    if "live_canary_retry_required" in blocking_set:
        steps.append(
            "Refresh the expired Facebook Page token if needed, rerun execute-mode Facebook validation, and retry the approved live canary publish."
        )
    if "live_canary_execution_missing" in blocking_set:
        steps.append("Execute one real canary chain against the owned WordPress and Facebook environments and then review health plus tracking outputs.")
    return tuple(steps)


def _latest_non_empty(*values: str | None) -> str | None:
    normalized = [value for value in values if value]
    return max(normalized) if normalized else None


def _mask_value(value: str) -> str | None:
    if not value:
        return None
    if len(value) <= 6:
        return value
    return f"{value[:3]}...{value[-3:]}"
