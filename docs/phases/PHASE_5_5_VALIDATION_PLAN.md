# Phase 5.5 Validation Plan

## Purpose

This plan defines how approval automation earns trust.

Autoapproval should be treated like a safety-critical feature for this business, because one bad automated publish can damage trust faster than many slow manual reviews.

## Required Validation Baseline

### 1. Score-to-review comparison

Shadow mode must prove:

1. automated recommendations are explainable,
2. disagreement with operator review is low enough to justify a narrow live lane,
3. false positives are measured explicitly.

### 2. Hard-block enforcement

The system must prove that autoapproval cannot bypass:

1. blocked quality states,
2. derivative-risk blocks,
3. weak-fit routing blocks,
4. missing media-review requirements where applicable.

### 3. Override and rollback rehearsal

The operator must prove:

1. autoapproval can be disabled,
2. an automated approval can be reversed,
3. the audit trail still shows what happened.

### 4. Acceptance evidence

Before the phase closes, the repo should contain:

1. shadow-mode evidence,
2. false-positive review,
3. rollback evidence,
4. explicit lane definitions for what is and is not allowed.

## Failure Conditions

Phase 5.5 should remain open if:

1. score reasons are opaque,
2. disagreement rates are still too high,
3. rollback is not immediate,
4. the operator cannot clearly inspect why an item was autoapproved.
