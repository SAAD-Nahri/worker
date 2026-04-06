# Phase 4.6 Execution Plan

## Purpose

This document turns the AI-assisted content-quality phase into explicit implementation work without letting it drift into full-content generation.

The goal is to improve bounded text quality after activation is proven, while keeping the heuristic and deterministic baselines intact.

## Execution Principle

Provider-backed AI should enter as an optional quality layer behind the existing micro-skill interface.

It must not become a new architectural center.

## Slice 1: Provider Configuration Layer

### Objective

Define how an operator enables the first optional provider safely.

### Deliverables

1. OpenAI-first provider config policy,
2. preferred `OPENAI_API_KEY` local-secret path,
3. optional ignored local config fallback,
4. explicit non-required provider behavior.

### Out Of Scope

1. CI secret injection,
2. multi-provider credential rotation,
3. cloud secret managers.

## Slice 2: Provider Adapter

### Objective

Add an OpenAI-backed provider implementation behind the existing `MicroSkillProvider` pattern.

### Deliverables

1. provider selection support in the CLI and micro-skill path,
2. OpenAI-backed implementation for the accepted bounded skills,
3. deterministic and heuristic fallback behavior when provider usage is not enabled.

### Out Of Scope

1. full-article generation,
2. source selection,
3. template selection,
4. autonomous publish or business decisions.

## Slice 3: Prompt And Output Contracts

### Objective

Make provider-backed outputs repeatable, bounded, and testable.

### Deliverables

1. prompt contracts for headline, intro, and excerpt tasks,
2. output-shape rules for each skill,
3. rejection and retry boundaries for weak provider output.

### Out Of Scope

1. giant prompts,
2. free-form chat behavior,
3. hidden provider-side behavior assumptions.

## Slice 4: Review And Logging Hardening

### Objective

Keep provider-backed wording review-safe and visible.

### Deliverables

1. accurate `model_label` logging for provider-backed output,
2. review-state reopening for content-affecting changes,
3. preserved fallback behavior when provider output is weak or unavailable.

### Out Of Scope

1. trusting provider text without review,
2. silently bypassing the heuristic path.

## Slice 5: Acceptance Replay

### Objective

Prove that provider-backed skills improve selected bounded fields without destabilizing the system.

### Deliverables

1. focused unit coverage,
2. acceptance comparison between heuristic and provider-backed outputs,
3. a written acceptance batch with cost and quality notes.

### Out Of Scope

1. large-scale editorial evaluation,
2. broad publish-volume testing.

## Exit Recommendation

Do not treat Phase 4.6 as complete because model calls work.

Close it only when:

1. the provider remains optional,
2. the fallback path remains operational,
3. bounded text quality improves in accepted use cases,
4. no drift toward full-article generation has been introduced.
