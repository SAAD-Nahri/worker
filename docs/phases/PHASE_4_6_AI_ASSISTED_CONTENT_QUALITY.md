# Phase 4.6: AI-Assisted Content Quality

## Objective

Add an optional OpenAI-backed quality layer after the deterministic workflow is already proven to work end to end.

This phase exists because the deterministic and heuristic baseline is good enough to build trust in the workflow, but it is not the final quality ceiling for:

1. headlines,
2. intros,
3. excerpts,
4. later bounded social-package refinement.

## Why This Phase Matters

The project should not depend on external AI before the connected system is proven.

Once the system is proven, bounded provider help can raise wording quality without replacing the source-first, template-first architecture.

This phase makes provider use explicit, review-safe, and optional instead of letting it enter the repo as random model calls.

## Main Responsibilities

1. add an optional OpenAI-backed provider path behind the existing micro-skill seam,
2. keep deterministic and heuristic fallback behavior intact,
3. improve bounded text quality for accepted draft micro-skill targets,
4. add manual Facebook package refinement as variant generation only,
5. define prompt contracts, output boundaries, retry rules, and failure handling,
6. make AI usage visible in runtime records, operator API payloads, and the approval UI.

## Required Outputs

1. optional provider-backed draft micro-skill integration,
2. manual social-package refinement CLI that appends review-safe variants without changing the selected package,
3. local-secret handling rules for provider credentials,
4. prompt and output contracts for allowed skills,
5. explicit fallback behavior when the provider is unavailable or weak,
6. review-visible AI provenance on draft and social detail surfaces.

Planning references:

1. [PHASE_4_6_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_6_EXECUTION_PLAN.md)
2. [PHASE_4_6_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_6_VALIDATION_PLAN.md)
3. [OPENAI_PROVIDER_CONFIG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/OPENAI_PROVIDER_CONFIG_POLICY_V1.md)
4. [AI_MICRO_SKILL_PROMPT_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AI_MICRO_SKILL_PROMPT_CONTRACTS_V1.md)
5. [PHASE_4_6_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_6_ACCEPTANCE_BATCH_1.md)

## What This Phase Must Not Do

1. turn the system into full AI article generation,
2. let external AI replace source selection,
3. let external AI replace template structure,
4. make the system unusable when the provider is unavailable,
5. silently auto-apply provider text into queue or transport workflows,
6. hide AI usage from review or audit layers.

## First Implemented Skills

The first implemented provider-backed tasks are:

1. `generate_headline_variants`
2. `generate_short_intro`
3. `generate_excerpt`
4. `refine_social_package_variants`

## Risks

1. model output can become generic or clicky,
2. costs can quietly expand,
3. weak prompts can create unstable quality,
4. drift toward field-by-field free editing can break the review workflow,
5. review can become too trusting if AI usage is not made explicit.

## Definition Of Done

Phase 4.6 is done when:

1. provider-backed draft micro-skills improve quality on approved bounded targets,
2. the deterministic and heuristic paths still keep the system operational with no OpenAI config,
3. manual social refinement only appends review-safe variant options and never changes the active package automatically,
4. AI usage is logged and review-visible,
5. the repo has explicit cost, failure, and review rules,
6. the project remains template-first instead of model-first.
