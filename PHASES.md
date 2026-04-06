# PHASES

This file translates the master plan into an execution sequence. Each phase has a purpose, entry condition, deliverable set, and exit condition. Work should not jump ahead without a clear reason.

## Phase Order

1. Phase 0: Foundation and Planning
2. Phase 1: Source Engine
3. Phase 2: Content Engine
4. Phase 3: Social Packaging + Distribution
5. Phase 4: Tracking Foundation
6. Phase 4.5: System Activation And Live Validation
7. Phase 4.6: AI-Assisted Content Quality
8. Phase 4.7: Media And Asset Layer
9. Phase 4.8: Runtime Operations And Deployment
10. Phase 4.9: Approval UI And Operator Console
11. Phase 5: Decision Layer
12. Phase 5.5: Approval Automation And Autopilot
13. Phase 6: Scaling Layer

## Phase 0: Foundation and Planning

**Purpose**

Create the documentation, boundaries, and operating rules required to build the system cleanly.

**Entry condition**

The project exists only as an idea and needs architectural grounding.

**Primary outputs**

1. master plan,
2. locked decisions,
3. phase definitions,
4. todo list,
5. open questions list,
6. phase briefs.

**Exit condition**

The team can begin Phase 1 without guessing what the system is supposed to be.

## Phase 1: Source Engine

**Purpose**

Build the intake layer that produces usable candidate content.

**Entry condition**

The planning docs exist and the initial source strategy is agreed.

**Primary outputs**

1. source registry shape,
2. fetch strategy,
3. cleaner requirements,
4. classifier requirements,
5. dedupe baseline,
6. source audit rules.

**Exit condition**

The system can reliably ingest and normalize candidate source items for the first niche.

## Phase 2: Content Engine

**Purpose**

Turn normalized source material into structured blog drafts through templates and controlled enhancement.

**Entry condition**

The Source Engine can produce stable candidate inputs.

**Primary outputs**

1. template library for blog output,
2. formatting engine requirements,
3. AI micro-skill definitions,
4. quality checks,
5. review-ready draft flow.

**Exit condition**

A sourced item can be transformed into a clean draft with predictable structure and visible review-ready state.

## Phase 3: Social Packaging + Distribution

**Purpose**

Publish approved content to WordPress and generate Facebook-ready assets from the blog draft.

**Entry condition**

The Content Engine can consistently produce reviewable drafts.

**Primary outputs**

1. WordPress publishing workflow,
2. Facebook packaging templates,
3. queue and approval workflow,
4. blog-to-Facebook mapping,
5. scheduled publish flow.

**Exit condition**

The system can move from source item to approved blog post to mapped Facebook post.

## Phase 4: Tracking Foundation

**Purpose**

Store enough structured data to understand what was published and to support later analysis.

**Entry condition**

The system can publish content to the blog and map it to Facebook.

**Primary outputs**

1. publish history model,
2. mapping records,
3. variant references,
4. basic logs,
5. reporting-ready identifiers.

**Exit condition**

The operator can trace a post from source item to blog output to Facebook output.

## Phase 4.5: System Activation And Live Validation

**Purpose**

Prove that the existing system can run in a real operator environment with live local config, real credential validation, and one controlled canary chain.

**Entry condition**

Phase 4 is closed for tracking-scope work, transport validation paths exist, and the operator has an owned WordPress environment plus an owned Facebook Page available for activation.

**Primary outputs**

1. local secrets and config policy,
2. safe example config files,
3. execute-mode WordPress and Facebook validation evidence,
4. one controlled canary run through the connected system,
5. operator activation runbook and acceptance evidence.

**Exit condition**

The operator can safely configure the system locally, validate live credentials without mutating content, and run one canary chain end to end without hidden contract breaks.

## Phase 4.6: AI-Assisted Content Quality

**Purpose**

Improve text quality through provider-backed micro-skills only after the system already works as a connected operator workflow.

**Entry condition**

Phase 4.5 activation is complete, and the system has a trusted live baseline that can be improved without guessing whether failures come from the workflow or the model.

**Primary outputs**

1. provider-backed micro-skill architecture,
2. explicit AI credential policy,
3. bounded prompt and output contracts,
4. deterministic fallback behavior,
5. review-safe text-quality improvements.

**Exit condition**

The system can use bounded external AI to improve selected text fields while still remaining operable, auditable, and template-first without the provider.

## Phase 4.7: Media And Asset Layer

**Purpose**

Add the visual/media baseline needed to make blog and Facebook outputs operationally complete.

**Entry condition**

The text workflow is activated, and the content-quality layer is stable enough that visual work can anchor to approved final copy and publish context.

**Primary outputs**

1. media source and rights policy,
2. asset review workflow,
3. media linkage model,
4. blog/Facebook asset handling baseline,
5. operator-usable visual workflow.

**Exit condition**

The system can attach reviewed, rights-safe media to the publish chain without guesswork.

## Phase 4.8: Runtime Operations And Deployment

**Purpose**

Lock the boring, repeatable production operating model for the finished system so it can run reliably without depending on the developer workstation.

**Entry condition**

Phases 4.5, 4.6, and 4.7 are complete or close enough that the real live workflow, bounded AI layer, and media baseline are known.

**Primary outputs**

1. runtime operating model,
2. deployment and scheduling policy,
3. backup and recovery policy,
4. operator runbook for daily, weekly, and incident workflows,
5. a defined recommendation for the first production host and scheduler.

**Exit condition**

The operator can explain where the system runs, how recurring jobs execute, how secrets and data are handled, how backups are taken, and how the system is restored after failure without guessing.

## Phase 4.9: Approval UI And Operator Console

**Purpose**

Build the first real operator review console so human approval has a stable home before later decision logic and approval automation are layered on top.

**Entry condition**

The repo already has working review and queue actions, and the team wants a serious operator-facing shell without creating a second workflow engine.

**Primary outputs**

1. internal operator API,
2. WordPress admin review plugin,
3. approval UI runbook,
4. validation baseline for review-safe UI actions,
5. explicit fast-lane placeholder with autoapproval still disabled.

**Exit condition**

The operator can review drafts, social packages, and queue items from one admin shell while the repo runtime remains the source of truth.

## Phase 5: Decision Layer

**Purpose**

Use accumulated operating data to improve what the system does next.

**Entry condition**

Phases 4.5, 4.6, 4.7, 4.8, and 4.9 are complete, and the system has enough stable history to compare sources, content types, packaging variants, later media/text patterns, and the real runtime operating path without guessing how the live operator flow works.

**Primary outputs**

1. winner detection rules,
2. source scoring logic,
3. pattern comparison methods,
4. promotion candidate logic.

**Exit condition**

The system can make limited data-backed prioritization decisions.

## Phase 5.5: Approval Automation And Autopilot

**Purpose**

Turn trusted scoring and review evidence into a narrow, explainable approval-automation layer without jumping straight to reckless autonomous publishing.

**Entry condition**

Phase 5 is complete enough that scoring and winner-signal logic are understandable, sparse-data guardrails exist, and the operator has a stable runtime model plus rollback path.

**Primary outputs**

1. autoapproval policy,
2. shadow-mode scoring and approval evidence,
3. narrow eligibility rules for automatic approval,
4. rollback and kill-switch rules,
5. operator-visible autopilot audit trail.

**Exit condition**

The system can automatically approve only tightly defined, high-confidence cases with explicit safety rules, visible reasons, and immediate rollback capability.

## Phase 6: Scaling Layer

**Purpose**

Scale what has already been proven to work.

**Entry condition**

The decision layer can identify promising repeatable patterns, and any approval automation intended to scale has already passed through Phase 5.5 guardrails.

**Primary outputs**

1. scaling rules,
2. promotion workflow,
3. channel expansion evaluation,
4. optional later-stage orchestration.

**Exit condition**

The system can grow volume or spend based on evidence rather than guesswork.

## Phase Gates

The project should only move forward when the current phase is stable enough to justify the next one.

A phase should not be treated as complete just because implementation exists. It should be treated as complete only when the implementation, validation baseline, operator workflow, documentation, and next-phase handoff are all explicit.

Reference:

1. [docs/phases/PHASE_GOVERNANCE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_GOVERNANCE.md)

### Gate questions

Before moving to the next phase, ask:

1. is the current phase producing reliable outputs,
2. are the contracts between components clear,
3. are the main risks understood,
4. are we adding the next layer because we need it, not because it is interesting,
5. does moving forward preserve the source-first, template-first architecture.

## Gate Artifacts

When possible, phase transitions should leave explicit artifacts, not just verbal confirmation.

Recommended artifacts:

1. a closeout review for the completed phase,
2. an entry checklist for the next phase,
3. a current validation baseline,
4. a short record of residual risks that are acceptable versus blockers.

## Minimum Closure Standard

Before a phase closes, the repository should be able to answer all of the following without guesswork:

1. what the phase delivered,
2. what commands prove the current baseline,
3. what files are authoritative inputs,
4. what files are generated runtime state,
5. how the operator safely runs and resets the phase,
6. what risks remain but are acceptable,
7. what the next phase is allowed to assume,
8. what the next phase must not redefine.

If those answers are missing, the phase is not closed yet.

## Phase Discipline

The most common failure mode for this project is phase skipping. The system should not jump to analytics, agents, or scaling while the source and formatting layers are still weak.

The next common failure mode is different:

1. assuming a well-tested internal machine is already a live operator-ready system.

Phase 4.5 exists to block that mistake.
