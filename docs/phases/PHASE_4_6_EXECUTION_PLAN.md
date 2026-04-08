# Phase 4.6 Execution Plan

## Purpose

This document turns the AI-assisted content-quality phase into explicit implementation work without letting it drift into full-content generation or transport automation.

The goal is to improve bounded text quality after activation is proven while keeping the heuristic and deterministic baselines intact.

## Execution Principle

Provider-backed AI enters as an optional quality layer behind existing seams.

It must not become a new architectural center, and it must never become a required runtime dependency for the rest of the repo.

## Slice 1: Provider Configuration Layer

### Objective

Define how an operator enables the first optional provider safely and locally.

### Deliverables

1. `OpenAIProviderConfig` loader,
2. preferred `OPENAI_API_KEY` secret path,
3. ignored `config/openai_provider_config.local.json` fallback,
4. file-backed `model` and `timeout_seconds` support,
5. explicit non-required provider behavior.

### Out Of Scope

1. CI secret injection,
2. multi-provider credential rotation,
3. cloud secret managers.

## Slice 2: Draft Provider Adapter

### Objective

Add an OpenAI-backed provider implementation behind the existing `MicroSkillProvider` pattern and keep `apply_micro_skills(...)` authoritative for normalization and review reopening.

### Deliverables

1. provider selection support in `apply_draft_micro_skills.py`,
2. OpenAI-backed implementation for `generate_headline_variants`, `generate_short_intro`, and `generate_excerpt`,
3. one retry on weak or invalid output,
4. deterministic and heuristic fallback behavior when provider usage is not enabled or not strong enough.

### Out Of Scope

1. full-article generation,
2. source selection,
3. template selection,
4. autonomous publish or business decisions.

## Slice 3: Prompt And Output Contracts

### Objective

Make provider-backed outputs repeatable, bounded, testable, and review-safe.

### Deliverables

1. prompt contracts for headline, intro, and excerpt tasks,
2. output-shape rules for each skill,
3. rejection and retry boundaries for weak provider output,
4. prompt contracts for manual social-package refinement as full package bundles.

### Out Of Scope

1. giant prompts,
2. free-form chat behavior,
3. hidden provider-side behavior assumptions.

## Slice 4: Manual Social Refinement

### Objective

Add review-safe Facebook package refinement without weakening deterministic packaging.

### Deliverables

1. keep `prepare_facebook_package` deterministic and unchanged,
2. add `python src\cli\refine_social_package.py --social-package-id <id> --provider openai`,
3. request 1-2 package variants containing `hook_text`, `caption_text`, and `comment_cta_text` together,
4. append provider-generated variants into `variant_options` with `openai_*` labels,
5. leave the selected variant and current approval state unchanged during generation.

### Out Of Scope

1. auto-application of provider output,
2. transport execution,
3. in-plugin generation buttons.

## Slice 5: Review And Logging Hardening

### Objective

Keep provider-backed wording review-safe and visible.

### Deliverables

1. accurate `model_label` logging for provider-backed draft output,
2. matching AI assistance metadata on `SocialPackageRecord`,
3. review-state reopening for content-affecting draft changes,
4. operator API and plugin detail visibility for draft and social AI provenance,
5. preserved fallback behavior when provider output is weak or unavailable.

### Out Of Scope

1. trusting provider text without review,
2. silently bypassing the heuristic path,
3. mutating approved package selection during variant generation.

## Slice 6: Acceptance Replay

### Objective

Prove that provider-backed skills improve selected bounded fields without destabilizing the system.

### Deliverables

1. focused unit coverage,
2. acceptance comparison between heuristic and provider-backed outputs,
3. a written acceptance batch with fallback and cost notes.

### Out Of Scope

1. large-scale editorial evaluation,
2. broad publish-volume testing,
3. live cost benchmarking with real spend during automated tests.

## Exit Recommendation

Do not treat Phase 4.6 as complete because model calls work.

Close it only when:

1. the provider remains optional,
2. the fallback path remains operational,
3. bounded text quality improves in accepted use cases,
4. social refinement remains manual and review-safe,
5. no drift toward full-article generation or transport automation has been introduced.
