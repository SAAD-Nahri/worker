# Phase 5.5 Execution Plan

## Purpose

This plan defines how approval automation should be introduced without weakening the project.

The correct build order is:

1. shadow mode first,
2. narrow autoapproval lanes second,
3. live autopilot only after evidence,
4. scaling only after rollback and override paths are proven.

## Recommended Build Order

### Slice 1: Policy and lane definition

Define:

1. which content families are even eligible,
2. which score inputs are allowed,
3. which hard blocks still override score.

### Slice 2: Shadow mode

Run scoring in advisory mode only:

1. no live autoapproval,
2. compare score recommendations against real operator decisions,
3. measure false positives and operator disagreement.

### Slice 3: Narrow live autoapproval

Enable only limited lanes:

1. clearly structured content families,
2. strong quality and derivative-safe results,
3. known-safe distribution path,
4. explicit confidence threshold.

### Slice 4: Override and rollback

Before broader use, prove:

1. the operator can override an automated approval,
2. autopilot can be disabled quickly,
3. the audit trail remains readable.

## Default Recommendation

Do not begin with automatic public publishing for all content.

Begin with:

1. shadow-mode recommendations,
2. then autoapproval for a small lane,
3. then optional autoqueue,
4. only later consider broader autopilot.
