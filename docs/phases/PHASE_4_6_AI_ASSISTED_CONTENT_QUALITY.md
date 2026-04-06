# Phase 4.6: AI-Assisted Content Quality

## Objective

Improve wording quality and packaging quality after the system is already proven to work end to end.

This phase exists because the current deterministic and heuristic baseline is good enough to build trust in the workflow, but it is not the final quality ceiling for:

1. headlines,
2. intros,
3. excerpts,
4. short section smoothing,
5. later social packaging improvements.

## Why This Phase Matters

The project should not depend on external AI before the connected system is proven.

But once the system is proven, better bounded AI can raise output quality without replacing the source-first, template-first architecture.

This phase makes that future improvement explicit and controlled instead of letting it enter the repo as random model calls.

## Main Responsibilities

1. define the provider-backed micro-skill architecture,
2. keep deterministic and heuristic fallback behavior intact,
3. improve bounded text quality for accepted micro-skill targets,
4. define prompt contracts, output boundaries, and review rules,
5. define cost controls and failure handling,
6. define AI usage logging and auditability.

## Required Outputs

1. optional provider-backed micro-skill integration,
2. local-secret handling rules for provider credentials,
3. prompt and output contracts for allowed skills,
4. explicit fallback behavior when the provider is unavailable or weak,
5. updated review and quality rules for AI-assisted text.

Planning references:

1. [PHASE_4_6_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_6_EXECUTION_PLAN.md)
2. [PHASE_4_6_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_6_VALIDATION_PLAN.md)
3. [OPENAI_PROVIDER_CONFIG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/OPENAI_PROVIDER_CONFIG_POLICY_V1.md)
4. [AI_MICRO_SKILL_PROMPT_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AI_MICRO_SKILL_PROMPT_CONTRACTS_V1.md)

## What This Phase Must Not Do

1. turn the system into full AI article generation,
2. let external AI replace source selection,
3. let external AI replace template structure,
4. make the system unusable when the provider is unavailable,
5. hide AI usage from review or audit layers.

## Candidate First Skills

The likely first provider-backed skills are:

1. `generate_headline_variants`
2. `generate_short_intro`
3. `generate_excerpt`
4. `smooth_section_copy`
5. later limited Facebook hook and caption refinement

## Risks

1. model output can become generic or clicky,
2. costs can quietly expand,
3. weak prompts can create unstable quality,
4. drift toward full-article generation can break the project architecture,
5. review can become too trusting if AI usage is not made explicit.

## Definition Of Done

Phase 4.6 is done when:

1. provider-backed micro-skills improve quality on approved bounded targets,
2. the deterministic fallback path still keeps the system operational,
3. AI usage is logged and review-visible,
4. the repo has explicit cost, failure, and review rules,
5. the project remains template-first instead of model-first.
