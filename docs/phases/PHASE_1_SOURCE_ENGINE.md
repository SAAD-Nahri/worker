# Phase 1: Source Engine

## Objective

Build the intake foundation that can reliably produce usable source candidates for the food-facts niche.

## Why This Phase Comes First

Source selection is the highest-leverage part of the project. If the source layer is weak, the content engine, social packaging, and monetization layers will all be weak. This phase determines the quality ceiling of the entire system.

## Main Responsibilities

1. define the source registry,
2. define the fetch workflow,
3. define RSS-first intake,
4. define selective scraping boundaries,
5. define normalized source records,
6. define classification and dedupe requirements,
7. define source audit logging.

## Required Outputs

1. source registry schema,
2. source metadata model,
3. intake workflow definition,
4. normalized source item shape,
5. dedupe approach,
6. source quality rules,
7. source acceptance and retirement criteria.

## Key Decisions To Make

1. what counts as a valid source,
2. how source families are grouped,
3. what fields are required on every source item,
4. what freshness means for this niche,
5. how much duplication is acceptable,
6. what the first candidate source set should be.

## Things This Phase Must Not Do

1. build the blog publisher,
2. build Facebook posting workflows,
3. build full AI generation,
4. add advanced analytics,
5. design agent orchestration.

## Risks

1. choosing noisy or weak sources,
2. overcomplicating the fetch model,
3. under-defining normalized source structure,
4. ignoring dedupe until later,
5. relying on one source family.

## Definition Of Done

Phase 1 is done when:

1. the first source registry is clearly defined,
2. intake rules are stable,
3. the team knows what a normalized source item looks like,
4. the system can move clean inputs into the Content Engine.

## Current Status

The current baseline is no longer theoretical.

The repository now has a working Source Engine slice that already covers:

1. registry loading from [data/source_registry.json](C:/Users/Administrator/OneDrive/Documents/co_ma/data/source_registry.json),
2. live RSS intake for the active source set,
3. normalized source item creation,
4. deterministic classification and dedupe,
5. optional article-page body extraction with strict domain boundaries,
6. source-status validation and intake gating,
7. recorded source-review decisions with optional registry updates,
8. explicit fallback handling for degraded RSS and non-RSS manual sources,
9. source-health reporting from runtime state,
10. archive-first runtime reset for local clean runs,
11. append-only run history and source item logging,
12. CLI entry points for repeated manual runs.

The current implementation entry points are:

1. [src/source_engine](C:/Users/Administrator/OneDrive/Documents/co_ma/src/source_engine)
2. [src/cli/run_source_intake.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/run_source_intake.py)
3. [docs/execution/SOURCE_ENGINE_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/SOURCE_ENGINE_RUNBOOK.md)

## Phase 1 Completion

Phase 1 is now complete enough to hand off cleanly to Phase 2.

The Source Engine contract is now strong enough that downstream work can assume:

1. sources are registry-controlled,
2. intake is RSS-first,
3. degraded or non-RSS sources fail into explicit manual review modes instead of silent crawler expansion,
4. source status decisions are recorded,
5. operator reporting and reset workflows exist.

## Handoff To Phase 2

Phase 2 should treat the Source Engine as its upstream contract. It should assume source items are already cleaned enough to be structured, but not yet blog-ready.

Formal closure for this phase is recorded in [PHASE_1_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_1_CLOSEOUT.md).
