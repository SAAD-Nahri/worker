# Distribution Health Reporting V1

## Purpose

This document defines the first operator-facing health report for Phase 3 distribution state.

The report exists to answer practical questions such as:

1. which approved drafts have become usable WordPress publish chains,
2. which blog items still need Facebook packaging or social review,
3. which publish chains have failed,
4. which scheduled items collide,
5. which publish, queue, or mapping states are inconsistent enough to require manual review.

## Core Rule

The health report is not a replacement for append-only runtime records.

It is a derived operator summary built from:

1. `blog_publish_records.jsonl`
2. `social_package_records.jsonl`
3. `social_package_reviews.jsonl`
4. `facebook_publish_records.jsonl`
5. `queue_item_records.jsonl`
6. `blog_facebook_mapping_records.jsonl`

The report must make the current state easier to operate without inventing new hidden state.

## Required Output Layers

The report should provide:

1. a summary layer with counts and operator alert totals,
2. one row per latest `blog_publish_id` chain,
3. explicit collision and consistency alerts,
4. enough detail to explain failure or scheduling review work without opening raw JSONL files first.

## Summary Requirements

The summary must preserve at minimum:

1. latest snapshot timestamp,
2. total blog publish chains,
3. WordPress status counts,
4. social approval counts,
5. Facebook publish status counts,
6. blog queue state counts,
7. Facebook queue state counts,
8. mapping status counts,
9. operator signal counts,
10. coverage counts for social packages, confirmed blog URLs, remote WordPress post ids, and Facebook post ids,
11. row counts with consistency issues,
12. row counts with schedule alerts,
13. aggregated consistency-issue counts,
14. aggregated schedule-alert counts,
15. top visible error messages.

## Row Requirements

Each row should preserve at minimum:

1. `blog_publish_id`
2. `draft_id`
3. `source_item_id`
4. `wordpress_title`
5. `wordpress_status`
6. `scheduled_for_blog`
7. `blog_queue_state`
8. `social_package_id`
9. `social_approval_state`
10. `social_review_count`
11. `latest_social_review_outcome`
12. `facebook_publish_id`
13. `facebook_publish_status`
14. `scheduled_for_facebook`
15. `facebook_queue_state`
16. `mapping_status`
17. `has_remote_wordpress_post`
18. `has_confirmed_blog_url`
19. `has_facebook_post_id`
20. `last_blog_error`
21. `last_facebook_error`
22. `latest_updated_at`
23. `operator_signal`
24. `consistency_issues`
25. `schedule_alerts`

## Operator Signal Rule

The operator signal should describe the primary workflow state, not every possible alert.

Examples:

1. `ready_for_wordpress`
2. `ready_for_social_review`
3. `ready_for_blog_schedule`
4. `ready_for_facebook_publish`
5. `ready_for_facebook_schedule`
6. `published_facebook`
7. `blog_publish_failed`
8. `facebook_publish_failed`
9. `state_incomplete`

Collision and consistency alerts should remain separate fields so the workflow state and the review warnings do not get conflated.

## Schedule Alert Rules

The v1 report should at minimum surface:

1. `blog_schedule_collision`
2. `facebook_schedule_collision`

Collision rules:

1. a blog collision exists when more than one latest blog publish chain is currently in `scheduled_blog` with the same `scheduled_for_blog` timestamp,
2. a Facebook collision exists when more than one latest blog publish chain is currently in `scheduled_facebook` with the same `scheduled_for_facebook` timestamp,
3. collisions are operator-review signals, not automatic blockers in v1,
4. collisions should stay visible in the report until the underlying runtime snapshots change.

## Consistency Issue Rules

The v1 report should at minimum surface obvious broken-chain conditions such as:

1. `missing_workflow_state`
2. `published_blog_missing_url`
3. `scheduled_blog_missing_time`
4. `blog_queue_state_mismatch`
5. `published_facebook_missing_post_id`
6. `scheduled_facebook_missing_time`
7. `facebook_queue_state_mismatch`
8. `mapping_status_mismatch`
9. `facebook_queue_missing_publish_record`
10. `mapping_missing_publish_record`
11. `facebook_publish_without_social_package`
12. `mapping_social_state_without_package`
13. `mapping_missing_social_linkage`
14. `approved_social_queue_mismatch`
15. `facebook_schedule_before_blog`

These issues should be derived from the latest append-only records, not from hidden repair logic.

## Scope Limits

This report does not yet try to become:

1. a publishing calendar UI,
2. a retry scheduler,
3. a dashboard for clicks or revenue,
4. a long-term analytics warehouse,
5. a replacement for the raw audit trail.

## CLI Rule

The operator entry point should remain:

`python src\cli\summarize_distribution_health.py`

JSON output should remain available for future automation:

`python src\cli\summarize_distribution_health.py --json`

## Definition Of Done

This spec is satisfied when:

1. the repo has an operator-facing distribution summary,
2. the summary exposes schedule collisions clearly,
3. the summary exposes broken publish-chain states clearly,
4. the report is derived from append-only runtime records instead of inventing a parallel state system.
