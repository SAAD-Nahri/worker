# LOCKED_DECISIONS

This file captures the current non-negotiable defaults for v1. These decisions should be treated as locked unless there is a strong reason to change them and the change is reflected in `MASTER_PLAN.md`.

## V1 Locked Decisions

1. First niche: food facts.
2. First language: English only.
3. First distribution target: Facebook Page.
4. Facebook Groups are deferred to a later phase.
5. Blog platform for v1: WordPress.
6. Publishing mode: scheduled queue with human approval.
7. Source strategy: curated source registry, RSS-first, selective scraping second.
8. Tracking in v1: blog publish history plus Facebook post mapping.
9. Paid amplification is a later-stage goal.
10. OpenClaw is deferred for later decision and optimization phases.
11. agency-agents is deferred as a future role library, not a v1 dependency.
12. First build priority: Source Engine.
13. Second build priority: Content Engine.
14. Third build priority: Social Packaging and Distribution.
15. First optional external AI provider after activation: OpenAI, while heuristic fallback remains mandatory.
16. First media baseline after activation: mixed `owned`, `licensed`, and `ai_generated` assets with explicit provenance and manual review.
17. Autoapproval and autopublish are deferred until after the Decision Layer, shadow-mode validation, and explicit rollback rules exist.

## Locked Production Model

The production model for v1 is:

Retrieval -> Cleaning -> Template Formatting -> Light AI Enhancement

This means:

1. no full-article AI generation for v1,
2. no replacing templates with giant prompts,
3. no unconstrained writing engine,
4. AI is allowed only for tightly scoped micro-tasks.

## Locked Principles

The project must preserve these principles:

1. simplicity over complexity,
2. source quality matters more than model quality,
3. formatting matters more than unconstrained generation,
4. distribution is the main driver of revenue,
5. data comes before intelligence,
6. deterministic systems come before AI orchestration,
7. templates matter more than giant prompts,
8. this is a formatting machine, not a free-form content generator,
9. the system should be cheap, maintainable, and understandable by one person,
10. overengineering early can kill the project.

## Explicitly Not In V1

The following are intentionally excluded from the first working version:

1. OpenClaw-centered orchestration,
2. large multi-agent workflows,
3. full custom CMS or custom blog platform work,
4. multilingual rollout,
5. Facebook Groups as a primary channel,
6. paid amplification,
7. heavy analytics or BI,
8. predictive winner modeling,
9. fully autonomous publishing,
10. full AI article generation.

## Change Control

If a locked decision needs to change:

1. document why the current decision is no longer valid,
2. document the expected impact on cost, complexity, and risk,
3. update `MASTER_PLAN.md`,
4. update this file,
5. update the affected phase brief and todo list.

No implementation should quietly override this file.
