from __future__ import annotations

from collections import Counter, defaultdict

from tracking_engine.models import (
    PublishChainSnapshot,
    PublishExceptionRow,
    PublishExceptionSummary,
    SourceTemplateActivitySummary,
    VariantUsageSummary,
)


NON_EXCEPTION_CHAIN_STATUSES = frozenset({"published_facebook", "scheduled_facebook", "monitor"})


def build_publish_exception_report(
    snapshots: list[PublishChainSnapshot],
) -> tuple[PublishExceptionSummary, list[PublishExceptionRow]]:
    rows: list[PublishExceptionRow] = []
    reason_counts: Counter[str] = Counter()
    failed_chain_count = 0
    partial_chain_count = 0
    consistency_issue_chains = 0
    schedule_alert_chains = 0

    for snapshot in snapshots:
        reasons = _resolve_exception_reasons(snapshot)
        if not reasons:
            continue
        if "blog_publish_failed" in reasons or "facebook_publish_failed" in reasons:
            failed_chain_count += 1
        else:
            partial_chain_count += 1
        if snapshot.consistency_issues:
            consistency_issue_chains += 1
        if snapshot.schedule_alerts:
            schedule_alert_chains += 1
        reason_counts.update(reasons)
        rows.append(
            PublishExceptionRow(
                chain_id=snapshot.chain_id,
                source_item_id=snapshot.source_item_id,
                draft_id=snapshot.draft_id,
                blog_publish_id=snapshot.blog_publish_id,
                social_package_id=snapshot.social_package_id,
                facebook_publish_id=snapshot.facebook_publish_id,
                source_family=snapshot.source_family,
                template_family=snapshot.template_family,
                category=snapshot.category,
                wordpress_status=snapshot.wordpress_status,
                facebook_publish_status=snapshot.facebook_publish_status,
                chain_status=snapshot.chain_status,
                exception_reasons=tuple(reasons),
                consistency_issues=snapshot.consistency_issues,
                schedule_alerts=snapshot.schedule_alerts,
                latest_activity_at=snapshot.latest_activity_at,
            )
        )

    summary = PublishExceptionSummary(
        total_exception_chains=len(rows),
        failed_chain_count=failed_chain_count,
        partial_chain_count=partial_chain_count,
        consistency_issue_chains=consistency_issue_chains,
        schedule_alert_chains=schedule_alert_chains,
        exception_reason_counts=dict(reason_counts),
    )
    return summary, rows


def build_variant_usage_summary(snapshots: list[PublishChainSnapshot]) -> VariantUsageSummary:
    selected_variant_label_counts = Counter(
        snapshot.selected_variant_label
        for snapshot in snapshots
        if snapshot.selected_variant_label
    )
    blog_titles_by_template_family = _nested_value_counts(
        snapshots,
        outer_key=lambda snapshot: snapshot.template_family or "unknown",
        value_key=lambda snapshot: snapshot.selected_blog_title,
    )
    hooks_by_package_template = _nested_value_counts(
        snapshots,
        outer_key=lambda snapshot: snapshot.package_template_id or "none",
        value_key=lambda snapshot: snapshot.selected_hook_text,
    )
    captions_by_package_template = _nested_value_counts(
        snapshots,
        outer_key=lambda snapshot: snapshot.package_template_id or "none",
        value_key=lambda snapshot: snapshot.selected_caption_text,
    )
    comment_ctas_by_comment_template = _nested_value_counts(
        snapshots,
        outer_key=lambda snapshot: snapshot.comment_template_id or "none",
        value_key=lambda snapshot: snapshot.selected_comment_cta_text,
    )

    return VariantUsageSummary(
        total_chains=len(snapshots),
        chains_with_headline_variants=sum(1 for snapshot in snapshots if snapshot.headline_variants_count > 0),
        selected_variant_label_counts=dict(selected_variant_label_counts),
        blog_title_counts_by_template_family=blog_titles_by_template_family,
        hook_counts_by_package_template=hooks_by_package_template,
        caption_counts_by_package_template=captions_by_package_template,
        comment_cta_counts_by_comment_template=comment_ctas_by_comment_template,
    )


def build_source_template_activity_summary(snapshots: list[PublishChainSnapshot]) -> SourceTemplateActivitySummary:
    return SourceTemplateActivitySummary(
        total_chains=len(snapshots),
        counts_by_source_id=dict(Counter(snapshot.source_id or "unknown" for snapshot in snapshots)),
        counts_by_source_family=dict(Counter(snapshot.source_family or "unknown" for snapshot in snapshots)),
        counts_by_template_id=dict(Counter(snapshot.template_id or "unknown" for snapshot in snapshots)),
        counts_by_template_family=dict(Counter(snapshot.template_family or "unknown" for snapshot in snapshots)),
        counts_by_category=dict(Counter(snapshot.category or "unknown" for snapshot in snapshots)),
    )


def _resolve_exception_reasons(snapshot: PublishChainSnapshot) -> list[str]:
    reasons: list[str] = []
    if snapshot.chain_status == "blog_publish_failed" or snapshot.wordpress_status == "failed":
        reasons.append("blog_publish_failed")
    if snapshot.chain_status == "facebook_publish_failed" or snapshot.facebook_publish_status == "failed":
        reasons.append("facebook_publish_failed")
    if snapshot.consistency_issues:
        reasons.append("consistency_issue")
    if snapshot.schedule_alerts:
        reasons.append("schedule_alert")
    if snapshot.social_approval_state == "needs_edits":
        reasons.append("social_needs_edits")
    if snapshot.social_approval_state == "rejected":
        reasons.append("social_rejected")
    if snapshot.social_package_id is None:
        reasons.append("social_package_missing")
    elif snapshot.facebook_publish_id is None and snapshot.chain_status not in NON_EXCEPTION_CHAIN_STATUSES:
        reasons.append("facebook_publish_pending")
    if snapshot.wordpress_status not in {"scheduled", "published"}:
        reasons.append("blog_not_finalized")
    return list(dict.fromkeys(reasons))


def _nested_value_counts(
    snapshots: list[PublishChainSnapshot],
    *,
    outer_key,
    value_key,
) -> dict[str, dict[str, int]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for snapshot in snapshots:
        value = value_key(snapshot)
        if not value:
            continue
        grouped[outer_key(snapshot)][value] += 1
    return {
        key: dict(counter)
        for key, counter in grouped.items()
    }
