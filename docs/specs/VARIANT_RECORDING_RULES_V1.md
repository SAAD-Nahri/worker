# Variant Recording Rules V1

## Purpose

This document defines how Phase 4 should record selected content variants without overbuilding experimentation infrastructure.

The goal is to preserve what was chosen and shown publicly, even when the current runtime models do not yet carry perfect variant IDs.

## Core Rule

V1 variant tracking is selection-focused, not experiment-platform-focused.

Phase 4 must preserve:

1. what text was selected,
2. what template family produced it,
3. what candidate pool it came from when available.

It does not need:

1. full experiment assignment IDs,
2. statistical testing metadata,
3. cross-session variant weighting logic.

## Existing Variant-Like Fields In Runtime Records

### Draft layer

1. `DraftRecord.headline_selected`
2. `DraftRecord.headline_variants`
3. `DraftRecord.template_id`
4. `DraftRecord.template_family`

### Blog publish layer

1. `BlogPublishRecord.wordpress_title`
2. `BlogPublishRecord.template_id`

### Social package layer

1. `SocialPackageRecord.package_template_id`
2. `SocialPackageRecord.comment_template_id`
3. `SocialPackageRecord.hook_text`
4. `SocialPackageRecord.caption_text`
5. `SocialPackageRecord.comment_cta_text`
6. `SocialPackageRecord.selected_variant_label`

### Mapping layer

1. `BlogFacebookMappingRecord.selected_blog_title`
2. `BlogFacebookMappingRecord.selected_hook_text`
3. `BlogFacebookMappingRecord.selected_caption_text`
4. `BlogFacebookMappingRecord.selected_comment_cta_text`

## Required Variant Slots

Phase 4 should explicitly normalize these selected variant slots:

1. `blog_title`
2. `facebook_hook`
3. `facebook_caption`
4. `facebook_comment_cta`

## Required Normalized Variant Fields

For each selected slot, preserve at minimum:

1. `variant_slot`
2. `selected_text`
3. `template_id_or_label`
4. `source_record_id`
5. `source_layer`
6. `candidate_count` when available
7. `selected_variant_label` when available

## Slot Rules

### 1. Blog title

Normalize from:

1. `BlogPublishRecord.wordpress_title` as the published selected text
2. `DraftRecord.headline_selected` as the upstream draft selection
3. `DraftRecord.headline_variants` as the candidate pool when present

Preferred source of truth for the final selected blog title:

1. mapping `selected_blog_title`
2. blog publish `wordpress_title`
3. draft `headline_selected`

### 2. Facebook hook

Normalize from:

1. mapping `selected_hook_text`
2. social package `hook_text`
3. social package `package_template_id`
4. social package `selected_variant_label`

### 3. Facebook caption

Normalize from:

1. mapping `selected_caption_text`
2. social package `caption_text`
3. social package `package_template_id`
4. social package `selected_variant_label`

### 4. Facebook comment CTA

Normalize from:

1. mapping `selected_comment_cta_text`
2. social package `comment_cta_text`
3. social package `comment_template_id`
4. social package `selected_variant_label`

## Synthetic Identity Rule

The current runtime baseline does not yet provide durable per-variant IDs for every selected output.

Phase 4 should therefore:

1. keep the selected text as the required value,
2. keep the template ID or selected-variant label when it exists,
3. avoid inventing fake UUID-style variant IDs that do not map back to a real runtime record.

If a synthetic tracking key is needed, it should be deterministic and derived from:

1. `variant_slot`
2. `source_record_id`
3. `selected_text`

## What Must Be Avoided

Do not:

1. drop the selected text and keep only a vague label,
2. pretend the current runtime carries stronger variant identity than it actually does,
3. force Phase 4 to become a full experiment platform,
4. overwrite selected published values with newer draft candidates.

## Known Gaps

These are real but acceptable current gaps:

1. headline candidate ordering is not yet preserved explicitly,
2. social-package records expose one selected package rather than a richer candidate pool,
3. selected variant labels are optional rather than universal,
4. publish records do not yet preserve richer actor or selection metadata for each slot.

## Definition Of Done

This spec is satisfied when:

1. Phase 4 can preserve the selected title, hook, caption, and comment CTA coherently,
2. the normalized tracking layer does not invent fake experiment complexity,
3. later winner analysis can still compare real selected outputs instead of empty labels.

## Current Baseline

The current repo now preserves selected title, hook, caption, and comment CTA values through the on-demand tracking layer.

What still remains deferred:

1. durable per-variant IDs,
2. richer stored candidate pools for social packaging,
3. experiment-style assignment metadata.
