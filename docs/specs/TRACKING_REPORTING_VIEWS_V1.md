# Tracking Reporting Views V1

## Purpose

This document defines the minimum operator-readable reports Phase 4 should provide on top of normalized tracking data.

The goal is not to build dashboards. The goal is to give the operator a small set of reliable views that answer:

1. what was published,
2. what is missing or broken,
3. what variants and source families are actually being used.

## Core Rule

Tracking reports must be derived from trusted lineage and normalized publish-history data.

They must not:

1. invent performance metrics that do not exist yet,
2. replace the underlying append-only records,
3. hide failures by showing only successful chains.

## Required Reporting Views

### 1. Publish Chain Ledger

Purpose:

1. show one row per `blog_publish_id`,
2. trace source item -> draft -> blog publish -> social package -> Facebook publish,
3. make latest platform and mapping state visible in one place.

Minimum columns:

1. `publish_chain_id`
2. `source_item_id`
3. `source_id`
4. `draft_id`
5. `blog_publish_id`
6. `social_package_id`
7. `facebook_publish_id`
8. `wordpress_status`
9. `facebook_publish_status`
10. `blog_queue_state`
11. `facebook_queue_state`
12. `mapping_status`
13. `wordpress_post_url`
14. `published_at_blog`
15. `published_at_facebook`

### 2. Publish Exception View

Purpose:

1. isolate failed, incomplete, or inconsistent chains,
2. support debugging without reading raw JSONL files,
3. highlight operator work rather than hide it.

Include rows where:

1. `wordpress_status` indicates failure,
2. `facebook_publish_status` indicates failure,
3. queue and mapping states disagree,
4. a publish identifier is missing when the state claims success,
5. a chain is partial and needs intervention.

### 3. Variant Usage Summary

Purpose:

1. show which title, hook, caption, and comment CTA selections are actually being used,
2. support later comparison work without pretending performance data already exists.

Minimum aggregations:

1. selected blog title counts by template family,
2. hook counts by package template,
3. caption counts by package template,
4. comment CTA counts by comment template,
5. selected-variant-label counts when present.

### 4. Source And Template Activity Summary

Purpose:

1. show what source families and template families are reaching publication,
2. help the operator sanity-check content mix before Phase 5.

Minimum aggregations:

1. counts by `source_id`
2. counts by `source_family`
3. counts by `template_id`
4. counts by `template_family`
5. counts by `category`

### 5. Existing Phase 3 Views To Reuse

Phase 4 should reuse, not redefine:

1. distribution health reporting,
2. distribution schedule reporting,
3. source health reporting,
4. draft health reporting.

Those are operational views. Phase 4 adds tracking views on top of them.

## Output Format

V1 reporting should support:

1. text summaries for operator readability,
2. JSON output for later machine use.

CSV export is optional and not required for the first Phase 4 slice.

## What These Views Do Not Need Yet

Do not add yet:

1. CTR,
2. traffic attribution,
3. ROI calculations,
4. winner scoring,
5. paid-boost recommendations.

Those belong to later phases once external performance data exists.

## Current Baseline

The current repo now has:

1. a normalized publish-chain ledger,
2. a dedicated exception view built on Phase 4 lineage,
3. a variant usage summary,
4. a source-and-template activity summary built from finalized publish history.

The remaining gap is not whether these views exist. It is whether they should remain derived on demand or later gain persisted normalization and audit support.

## What Must Be Avoided

Do not:

1. let Phase 4 become a dashboard project,
2. hide partial or failed chains,
3. build views that require performance data not yet collected,
4. redefine Phase 3 health reports instead of building on them.

## Definition Of Done

This spec is satisfied when:

1. the repo knows which Phase 4 reports are required,
2. the reports are grounded in normalized lineage,
3. the operator can inspect publish history and usage patterns without guesswork.
