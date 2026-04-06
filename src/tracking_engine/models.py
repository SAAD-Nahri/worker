from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PublishChainSnapshot:
    chain_id: str
    snapshot_generated_at: str
    snapshot_version: str
    source_item_id: str
    source_id: str
    source_name: str
    source_family: str
    source_title: str
    source_url: str
    canonical_url: str
    source_published_at: str | None
    source_dedupe_status: str
    draft_id: str
    template_id: str
    template_family: str
    draft_language: str
    draft_workflow_state: str
    draft_approval_state: str
    quality_gate_status: str
    derivative_risk_level: str
    category: str
    tag_candidates: tuple[str, ...]
    selected_blog_title: str
    headline_selected: str
    headline_variants_count: int
    blog_publish_id: str
    publish_intent: str
    wordpress_status: str
    wordpress_slug: str
    wordpress_category: str
    wordpress_tags: tuple[str, ...]
    wordpress_post_id: str | None
    wordpress_post_url: str | None
    published_at_blog: str | None
    last_blog_publish_result: str
    last_blog_publish_error: str | None
    social_package_id: str | None
    package_template_id: str | None
    comment_template_id: str | None
    target_destination: str | None
    social_approval_state: str | None
    selected_variant_label: str | None
    blog_url_used_in_package: str | None
    social_packaging_notes: str | None
    selected_hook_text: str
    selected_caption_text: str
    selected_comment_cta_text: str
    facebook_publish_id: str | None
    facebook_destination_type: str | None
    facebook_publish_status: str | None
    published_at_facebook: str | None
    last_facebook_publish_result: str | None
    last_facebook_publish_error: str | None
    blog_queue_state: str | None
    facebook_queue_state: str | None
    mapping_status: str | None
    draft_review_count: int
    latest_draft_review_outcome: str | None
    social_review_count: int
    latest_social_review_outcome: str | None
    has_confirmed_blog_url: bool
    has_facebook_publish_record: bool
    chain_status: str
    consistency_issues: tuple[str, ...]
    schedule_alerts: tuple[str, ...]
    latest_activity_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublishChainHistorySummary:
    latest_snapshot_at: str | None
    total_chains: int
    source_family_counts: dict[str, int]
    template_family_counts: dict[str, int]
    wordpress_status_counts: dict[str, int]
    facebook_publish_status_counts: dict[str, int]
    chain_status_counts: dict[str, int]
    chains_with_social_package: int
    chains_with_facebook_publish: int
    chains_with_confirmed_blog_url: int
    chains_with_consistency_issues: int
    chains_with_schedule_alerts: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublishExceptionRow:
    chain_id: str
    source_item_id: str
    draft_id: str
    blog_publish_id: str
    social_package_id: str | None
    facebook_publish_id: str | None
    source_family: str
    template_family: str
    category: str
    wordpress_status: str
    facebook_publish_status: str | None
    chain_status: str
    exception_reasons: tuple[str, ...]
    consistency_issues: tuple[str, ...]
    schedule_alerts: tuple[str, ...]
    latest_activity_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublishExceptionSummary:
    total_exception_chains: int
    failed_chain_count: int
    partial_chain_count: int
    consistency_issue_chains: int
    schedule_alert_chains: int
    exception_reason_counts: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VariantUsageSummary:
    total_chains: int
    chains_with_headline_variants: int
    selected_variant_label_counts: dict[str, int]
    blog_title_counts_by_template_family: dict[str, dict[str, int]]
    hook_counts_by_package_template: dict[str, dict[str, int]]
    caption_counts_by_package_template: dict[str, dict[str, int]]
    comment_cta_counts_by_comment_template: dict[str, dict[str, int]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceTemplateActivitySummary:
    total_chains: int
    counts_by_source_id: dict[str, int]
    counts_by_source_family: dict[str, int]
    counts_by_template_id: dict[str, int]
    counts_by_template_family: dict[str, int]
    counts_by_category: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrackingAuditRecord:
    event_id: str
    event_type: str
    entity_type: str
    entity_id: str
    chain_id: str | None
    event_status: str
    event_summary: str
    event_timestamp: str
    actor_label: str
    view_name: str | None = None
    execution_mode: str | None = None
    config_path: str | None = None
    total_chains: int | None = None
    exception_chain_count: int | None = None
    consistency_issue_chains: int | None = None
    schedule_alert_chains: int | None = None
    latest_snapshot_at: str | None = None
    validated_identity_id: str | None = None
    validated_identity_name: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrackingAuditSummary:
    latest_event_at: str | None
    total_events: int
    event_type_counts: dict[str, int]
    event_status_counts: dict[str, int]
    entity_type_counts: dict[str, int]
    normalization_run_count: int
    transport_validation_count: int
    failed_event_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
