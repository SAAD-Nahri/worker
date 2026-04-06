# Phase 5: Decision Layer

## Objective

Use stored operating data to improve source selection, formatting choices, and distribution choices.

## Why This Phase Matters

This is where the system starts learning from its own history. The point is not to create an "AI brain." The point is to improve the business loop using evidence.

## Main Responsibilities

1. define winner signals,
2. define source scoring logic,
3. define pattern comparison across titles, templates, and hooks,
4. define promotion candidate rules,
5. decide whether any reasoning-heavy tooling is justified.

## Current Planning Baseline

The current starting baseline for Phase 5 is now documented in:

1. [PHASE_4_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_CLOSEOUT.md)
2. [PHASE_4_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_RESIDUAL_ITEMS.md)
3. [PHASE_4_5_SYSTEM_ACTIVATION.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_SYSTEM_ACTIVATION.md)
4. [PHASE_4_6_AI_ASSISTED_CONTENT_QUALITY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_6_AI_ASSISTED_CONTENT_QUALITY.md)
5. [PHASE_4_7_MEDIA_AND_ASSET_LAYER.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_7_MEDIA_AND_ASSET_LAYER.md)
6. [PHASE_4_8_RUNTIME_OPERATIONS_AND_DEPLOYMENT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_8_RUNTIME_OPERATIONS_AND_DEPLOYMENT.md)
7. [PHASE_4_9_APPROVAL_UI_AND_OPERATOR_CONSOLE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_9_APPROVAL_UI_AND_OPERATOR_CONSOLE.md)
8. [PHASE_5_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_5_ENTRY_CHECKLIST.md)
9. [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md)

Current starting position:

1. Phase 5 architecture can be planned against the accepted Phase 4 tracking contract,
2. Phase 5 implementation is gated behind Phase 4.5 system activation,
3. Phase 5 implementation is also gated behind the later AI-quality, media, runtime-operations, and operator-console phases,
4. Phase 5 must start with sparse-data guardrails,
5. Phase 5 must not assume click or revenue data already exists.

The Decision Layer is not allowed to answer unresolved runtime questions such as where jobs run, how backups happen, or how the operator restores the system after failure. Those belong to Phase 4.8.

It is also not allowed to invent a later oversight surface for human review. That belongs to Phase 4.9.

## Required Outputs

1. a simple decision model,
2. source ranking inputs,
3. content pattern comparison rules,
4. winner candidate criteria,
5. guardrails for future intelligence features.

## Key Decisions To Make

1. what counts as a winner,
2. what degree of confidence is needed before changing priorities,
3. what decisions stay deterministic,
4. when later-stage reasoning tools are worth considering,
5. how to avoid overfitting early data.

## Things This Phase Must Not Do

1. make OpenClaw mandatory,
2. convert the system into agent-first architecture,
3. automate major business decisions without clear evidence,
4. confuse experimentation with production readiness.

## Risks

1. weak or noisy winner definitions,
2. making decisions from too little data,
3. ranking based on vanity signals,
4. adding heavy orchestration before it is justified.

## Definition Of Done

Phase 5 is done when:

1. the system can rank some sources or patterns better than blind guessing,
2. the decision rules are understandable,
3. the project still preserves its deterministic core.

## Handoff To Phase 5.5

If approval automation is desired, Phase 5 should hand off to Phase 5.5 first, not directly to scaling.

Phase 5.5 should only receive decision outputs that are:

1. explainable,
2. narrow enough to validate in shadow mode,
3. stable enough to justify limited automatic approval lanes.
