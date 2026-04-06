# V1 Implementation Target

## Purpose

This document defines the recommended implementation shape for the first working version.

The goal is to reduce architectural ambiguity before code starts. It does not choose the final framework or language, but it does define the shape the system should take.

## Recommendation

The recommended implementation target for v1 is:

**a modular monolith with one codebase, one primary data store, one scheduled job layer, and one operator-facing review surface**

This is the best fit for the project's constraints:

1. solo operator,
2. low-cost operation,
3. high need for maintainability,
4. need for clear internal boundaries,
5. no justification yet for distributed complexity.

## Why Not Microservices

Microservices are the wrong starting point because they would add:

1. deployment complexity,
2. coordination overhead,
3. unnecessary interface fragmentation,
4. extra debugging burden,
5. maintenance cost that the business has not earned.

The project does need separation of concerns, but it does not need distributed architecture.

## Required V1 Shape

The first working implementation should aim for:

1. one repository,
2. one main application boundary,
3. one primary backing store for operational records,
4. one scheduling mechanism,
5. one review surface for the operator,
6. clearly separated internal modules for each engine.

## Internal Modules To Preserve

Even inside a modular monolith, the following concerns should remain distinct:

1. Source Engine,
2. Content Engine,
3. Social Packaging Engine,
4. Distribution Engine,
5. Tracking layer,
6. AI skill layer,
7. review and queue management.

The internal separation matters because the system should be able to evolve later without becoming tangled.

## Operational Storage Recommendation

V1 should use:

1. one primary operational store for records and states,
2. optionally a simple seed-file approach for source definitions if helpful during early setup,
3. stable internal identifiers across all major entities.

The architecture should not depend on:

1. multiple databases,
2. event buses,
3. distributed queues,
4. service-to-service messaging.

## Scheduling Recommendation

V1 should use a simple scheduled-job model.

The system needs enough scheduling to:

1. pull sources,
2. prepare drafts,
3. manage queue timing,
4. publish approved content.

It does not need:

1. high-scale worker fleets,
2. stream-processing architecture,
3. complex task orchestration engines.

## Review Surface Recommendation

The operator needs one practical review surface for:

1. draft approval,
2. social package approval,
3. queue review,
4. publish-state visibility.

The exact interface can remain open for now, but the architecture should assume there is a single coherent review path, not scattered manual steps.

## External Integrations For V1

The only external publishing dependencies that matter for v1 are:

1. WordPress,
2. Facebook Page publishing.

Everything else should be treated as future work.

## What V1 Must Avoid

The implementation target must avoid:

1. agent-first orchestration,
2. OpenClaw as a foundational dependency,
3. microservice decomposition,
4. multi-channel expansion architecture,
5. overbuilt analytics infrastructure,
6. automation that bypasses the review model.

## What This Enables Later

A good modular monolith enables later evolution into:

1. smarter scoring,
2. stronger analytics,
3. more capable scheduling,
4. optional reasoning layers,
5. later service extraction only if truly needed.

## Definition Of Done

This spec is satisfied when implementation planning assumes:

1. one codebase,
2. clear internal module boundaries,
3. one primary data store,
4. one scheduling layer,
5. one operator review flow,
6. no premature distributed complexity.
