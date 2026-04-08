# Project Foundation

This repository started as a documentation-first planning space and now includes working baselines through Phase 4 plus an explicit Phase 4.5 activation gate before more system complexity is added.

The goal is to build a low-cost, always-on content operations system for a solo operator. The system is designed to:

1. find high-performing simple content from the web,
2. transform it into clean blog posts,
3. transform those blog posts into Facebook-ready distribution assets,
4. drive traffic from Facebook to the blog,
5. monetize that traffic through ads,
6. later identify winners and scale what works.

The repository is still docs-led. The documents remain the authority, and the current code exists to implement the approved phased scope rather than bypass it.

## Core Rule

This project is not an "AI writes everything" system.

It is a content operations, formatting, distribution, and optimization system built around:

1. source quality,
2. template-driven formatting,
3. controlled AI enhancement,
4. disciplined publishing,
5. later decision-making from data.

## Document Map

Use the following files in this order:

1. [MASTER_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/MASTER_PLAN.md)
   The long-term source of truth. Business logic, architecture, risks, constraints, and roadmap live here.

2. [LOCKED_DECISIONS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/LOCKED_DECISIONS.md)
   Non-negotiable v1 defaults and what is explicitly out of scope.

3. [PHASES.md](C:/Users/Administrator/OneDrive/Documents/co_ma/PHASES.md)
   The implementation sequence, phase boundaries, and exit criteria.

4. [TODO.md](C:/Users/Administrator/OneDrive/Documents/co_ma/TODO.md)
   The master execution checklist.

5. [OPEN_QUESTIONS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/OPEN_QUESTIONS.md)
   The unresolved questions that still matter.

6. Specs in [docs/specs](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs)
   Implementation-ready contracts for records, states, templates, and review logic.

7. Execution docs in [docs/execution](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution)
   The practical starting point for the first seed sources, intake review, and pilot cycle.

8. Phase briefs in [docs/phases](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases)
   Operational notes, entry gates, execution plans, and validation plans for each build stage.

9. [docs/phases/PHASE_GOVERNANCE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_GOVERNANCE.md)
   The rulebook for opening, closing, and handing off phases professionally.
10. [docs/phases/PHASE_2_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_RESIDUAL_ITEMS.md)
   The record of what is intentionally deferred from Phase 2 so closeout is not blocked by later-phase work.
11. [docs/phases/PHASE_4_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_EXECUTION_PLAN.md)
   The sequenced implementation plan for the Tracking Foundation.
12. [docs/phases/PHASE_4_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_VALIDATION_PLAN.md)
   The validation baseline for the first tracking layer.
13. [docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md)
   The explicit rule for why normalized publish-chain snapshots stay on demand for now and when persistence should be reconsidered later.
14. [docs/phases/PHASE_4_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_CLOSEOUT.md)
   The formal Phase 4 closeout review and the handoff baseline into system activation.
15. [docs/phases/PHASE_4_5_SYSTEM_ACTIVATION.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_SYSTEM_ACTIVATION.md)
   The activation gate that proves the repo can run in a real operator environment before more decision complexity is added.
16. [docs/specs/LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md)
   The policy for local API keys, application passwords, and transport config files.
17. [docs/execution/SYSTEM_ACTIVATION_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/SYSTEM_ACTIVATION_RUNBOOK.md)
   The practical runbook for local config setup, execute-mode validation, and the first canary run.
18. [docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_1.md)
   The current local pre-live activation evidence showing the connected canary-preparation path and the remaining live credential blocker.
19. [docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_2.md)
   The current readiness checkpoint showing the live activation signal, placeholder-config detection, and the exact remaining execute-mode blockers.
20. [docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_3.md)
   The current execute-mode checkpoint showing a validated Facebook Page and the remaining live WordPress authentication blocker.
21. [docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_4.md)
   The current live draft-sync checkpoint showing that remote draft creation now works and that the remaining stop point is public canary quality, not transport auth.
22. [docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_5.md)
   The replacement-canary checkpoint showing that the cleaner public candidate now exists as remote WordPress draft `25`.
23. [docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_6.md)
   The live reconciliation-and-publish checkpoint showing that the replacement canary is now truly published on WordPress and that the remaining blocker is an expired Facebook Page token.
24. [docs/specs/SYSTEM_ACTIVATION_READINESS_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/SYSTEM_ACTIVATION_READINESS_REPORTING_V1.md)
   The operator-facing contract for seeing what still blocks a real live activation pass.
25. [docs/specs/WORDPRESS_REMOTE_STATE_RECONCILIATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_REMOTE_STATE_RECONCILIATION_V1.md)
   The activation support spec for safely inspecting and reconciling real remote WordPress post state back into local append-only records.
26. [docs/phases/PHASE_4_6_AI_ASSISTED_CONTENT_QUALITY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_6_AI_ASSISTED_CONTENT_QUALITY.md)
   The planned quality-enhancement phase that adds bounded provider-backed AI only after activation is proven.
27. [docs/phases/PHASE_4_7_MEDIA_AND_ASSET_LAYER.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_7_MEDIA_AND_ASSET_LAYER.md)
   The planned media phase that makes visuals and asset handling part of the system instead of a missing side task.
28. [docs/phases/PHASE_4_8_RUNTIME_OPERATIONS_AND_DEPLOYMENT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_8_RUNTIME_OPERATIONS_AND_DEPLOYMENT.md)
   The runtime/deployment phase that decides the boring production operating model before the Decision Layer starts.
29. [docs/specs/RUNTIME_OPERATING_MODEL_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/RUNTIME_OPERATING_MODEL_V1.md)
   The recommended answer for how the finished system should actually run in production.
30. [docs/execution/OPERATIONS_AND_DEPLOYMENT_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/OPERATIONS_AND_DEPLOYMENT_RUNBOOK.md)
   The practical runbook for daily operations, deployment updates, backup checks, and failure recovery.
31. [docs/phases/PHASE_4_9_APPROVAL_UI_AND_OPERATOR_CONSOLE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_9_APPROVAL_UI_AND_OPERATOR_CONSOLE.md)
   The approval-console phase that gives human review a stable UI before later decision and autopilot work.
32. [docs/specs/OPERATOR_API_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/OPERATOR_API_CONTRACT_V1.md)
   The internal API contract that exposes review-safe operator workflows over the repo runtime.
33. [docs/specs/WORDPRESS_ADMIN_APPROVAL_PLUGIN_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_ADMIN_APPROVAL_PLUGIN_V1.md)
   The contract for the thin WordPress admin plugin that serves as the operator review shell.
34. [docs/execution/APPROVAL_UI_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/APPROVAL_UI_RUNBOOK.md)
   The practical runbook for starting the operator API, installing the plugin, and using the approval UI safely.
35. [docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_3.md)
   The dashboard hardening checkpoint showing that the approval console now surfaces recent review activity and current alert context instead of counts alone.
36. [docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_4.md)
   The queue-removal hardening checkpoint showing that items can now be explicitly removed from the current batch through the audited approval path.
37. [docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_5.md)
   The detail-context hardening checkpoint showing that the approval detail screens now expose the source, draft, blog, and mapping context needed for safer operator decisions.
38. [docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_6.md)
   The queue-actionability and dashboard-navigation checkpoint showing that blocked queue approvals are now explicit and that dashboard activity and alerts can move the operator into the correct review detail screen.
39. [docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_7.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_7.md)
   The live-validation support checkpoint showing that the plugin now has a dedicated Validation page backed by one operator-readiness endpoint instead of forcing manual guesswork across multiple screens.
40. [docs/phases/PHASE_5_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_5_ENTRY_CHECKLIST.md)
   The gate that controls when Decision Layer work can begin and what it must not assume.
41. [docs/phases/PHASE_5_5_APPROVAL_AUTOMATION_AND_AUTOPILOT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_5_5_APPROVAL_AUTOMATION_AND_AUTOPILOT.md)
   The later automation phase that turns strong scoring into narrow, explainable autoapproval instead of risky broad autopublish.
42. [docs/specs/AUTOAPPROVAL_AND_AUTOPILOT_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AUTOAPPROVAL_AND_AUTOPILOT_POLICY_V1.md)
   The policy that keeps human approval locked now and defines how approval automation can be introduced safely later.
43. [docs/specs/OPENAI_PROVIDER_CONFIG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/OPENAI_PROVIDER_CONFIG_POLICY_V1.md)
   The first provider-config policy for optional OpenAI-backed quality work.
44. [docs/specs/ASSET_RECORD_AND_LINKAGE_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/ASSET_RECORD_AND_LINKAGE_CONTRACT_V1.md)
   The first asset record contract for the later media phase.
45. [docs/specs/OPERATOR_API_RUNTIME_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/OPERATOR_API_RUNTIME_POLICY_V1.md)
   The runtime policy that explains how the operator API should run locally and in production once the approval plugin is active.

## How To Use This Repository

Before implementation starts:

1. read `MASTER_PLAN.md`,
2. confirm `LOCKED_DECISIONS.md`,
3. review `PHASES.md`,
4. read the relevant spec in `docs/specs`,
5. read the relevant execution doc in `docs/execution`,
6. work from `TODO.md`,
7. resolve only the open questions needed for the current phase.

During implementation:

1. do not skip phase order,
2. do not widen scope casually,
3. do not treat AI tooling as the foundation,
4. do not build platform expansion before the core loop works,
5. do not treat a phase as finished until its closeout and handoff artifacts exist.

## Current Starting Point

The current recommended path is:

1. treat Phase 0 as complete,
2. treat Phase 1 as operationally complete and use the source runbook plus registry as the accepted intake baseline,
3. treat Phase 2 as formally closed with explicit residual items recorded,
4. treat Phase 3 as formally closed with explicit residual items recorded,
5. treat Phase 4 as formally closed with explicit residual items recorded,
6. treat Phase 4.5 as the current activation gate before more complexity is added,
7. treat Phase 4.6 AI-assisted content quality as an implemented manual opt-in quality layer that still awaits formal phase closeout,
8. treat Phase 4.7 media and asset handling as an implemented operator-reviewed baseline that still awaits formal phase closeout,
9. treat Phase 4.8 runtime operations and deployment as a required future phase before the Decision Layer,
10. treat Phase 4.9 approval UI and operator console as a required future phase before the Decision Layer,
11. treat Phase 5.5 approval automation and autopilot as a required future phase after Decision Layer work proves strong scoring is trustworthy,
12. use [PHASE_4_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_CLOSEOUT.md), [PHASE_4_5_SYSTEM_ACTIVATION.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_SYSTEM_ACTIVATION.md), [PHASE_4_5_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_1.md), [PHASE_4_5_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_2.md), [PHASE_4_5_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_3.md), [PHASE_4_5_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_4.md), [PHASE_4_5_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_5.md), [PHASE_4_5_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_6.md), [WORDPRESS_REMOTE_STATE_RECONCILIATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_REMOTE_STATE_RECONCILIATION_V1.md), [PHASE_4_6_AI_ASSISTED_CONTENT_QUALITY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_6_AI_ASSISTED_CONTENT_QUALITY.md), [PHASE_4_6_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_6_ACCEPTANCE_BATCH_1.md), [PHASE_4_7_MEDIA_AND_ASSET_LAYER.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_7_MEDIA_AND_ASSET_LAYER.md), [PHASE_4_8_RUNTIME_OPERATIONS_AND_DEPLOYMENT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_8_RUNTIME_OPERATIONS_AND_DEPLOYMENT.md), [PHASE_4_9_APPROVAL_UI_AND_OPERATOR_CONSOLE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_9_APPROVAL_UI_AND_OPERATOR_CONSOLE.md), [OPERATOR_API_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/OPERATOR_API_CONTRACT_V1.md), [WORDPRESS_ADMIN_APPROVAL_PLUGIN_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_ADMIN_APPROVAL_PLUGIN_V1.md), [APPROVAL_UI_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/APPROVAL_UI_RUNBOOK.md), [PHASE_5_5_APPROVAL_AUTOMATION_AND_AUTOPILOT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_5_5_APPROVAL_AUTOMATION_AND_AUTOPILOT.md), [AUTOAPPROVAL_AND_AUTOPILOT_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AUTOAPPROVAL_AND_AUTOPILOT_POLICY_V1.md), [RUNTIME_OPERATING_MODEL_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/RUNTIME_OPERATING_MODEL_V1.md), [OPERATIONS_AND_DEPLOYMENT_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/OPERATIONS_AND_DEPLOYMENT_RUNBOOK.md), [LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md), [SYSTEM_ACTIVATION_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/SYSTEM_ACTIVATION_RUNBOOK.md), [PHASE_5_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_5_ENTRY_CHECKLIST.md), and [PHASE_6_SCALING_LAYER.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_6_SCALING_LAYER.md) as the current handoff baseline.

## Current Working Baseline

The current implemented slice covers:

1. application-facing source registry loading,
2. RSS intake across the active source set,
3. normalization, classification, and dedupe,
4. opt-in article-body extraction with domain boundaries and fallback behavior,
5. source-status validation and intake gating,
6. recorded source-review decisions with optional registry updates,
7. explicit fallback handling for degraded RSS and non-RSS manual sources,
8. source-health reporting from the registry plus latest runtime state,
9. archive-first runtime reset for local clean runs,
10. append-only intake history and item logging,
11. Phase 2 blog template contracts with accepted slot-level guidance encoded in application code,
12. Phase 2 draft-record models, section skeletons, template-based draft skeleton creation, and append-only draft storage foundations,
13. Phase 2 deterministic formatting from source item to structured draft record,
14. Phase 2 anchor extraction with boilerplate filtering and recipe/noise-aware candidate paragraph selection,
15. Phase 2 semantic-profile and content-fit signals for semantic anchor noise, noisy source context, and recipe-heavy source context,
16. Phase 2 weak-fit routing recommendations for `proceed`, `review_only`, `hold_for_reroute`, and `reject_for_v1`,
17. Phase 2 gold-set replay support for fixed semantic-anchor and routing acceptance cases,
18. Phase 2 controlled category and tag assignment from the approved v1 taxonomy,
19. Phase 2 quality evaluation with recorded pass, review-flag, or blocked outcomes plus derivative-risk notes,
20. Phase 2 slot-level template enforcement for section ranges, bullet-count expectations, and the food-fact early-answer rule,
21. Phase 2 structured draft review recording with approval-state transitions and append-only review logs,
22. Phase 2 bounded micro-skill enrichment for headline variants, intro tightening, and excerpt refinement, with title-shape-aware headline fallback, template-aware intro bounds, and weak-variant filtering,
23. Phase 2 post-review hardening so content-affecting intro rewrites refresh quality state and reopen review instead of leaving stale approvals behind,
24. Phase 2 operator-facing draft creation and draft-health reporting with visible routing recommendations,
25. Phase 2 closeout governance via an explicit closeout checklist,
26. Phase 3 local WordPress-ready payload preparation from approved drafts, including deterministic HTML rendering, slug generation, and append-only blog publish record storage,
27. Phase 3 deterministic Facebook package preparation from approved drafts, including family-specific hook, caption, and comment CTA derivation plus append-only social package record storage,
28. Phase 3 initial queue-record and blog-to-Facebook mapping baselines from local publish and packaging records,
29. Phase 3 manual social-package review logging and local WordPress publish-state update workflows with refreshed queue/mapping snapshots,
30. Phase 3 local Facebook publish-state records and update workflows with explicit `facebook_publish_id` tracking plus final queue/mapping-state progression,
31. Phase 3 conservative scheduling policy rules for manual versus auto scheduling, including explicit scheduling metadata and a reachable `ready_for_blog_schedule` queue state,
32. Phase 3 first real WordPress REST transport slice with application-password auth, dry-run request previews, remote draft create/update support, and append-only local success/failure recording,
33. Phase 3 first real Facebook Graph transport slice with dry-run request previews, Page feed publish/schedule support, and append-only local success/failure recording,
34. Phase 3 operator-facing distribution health reporting with visible queue, mapping, transport, schedule-collision, and broken-chain consistency signals,
35. Phase 3 non-mutating WordPress and Facebook transport-validation entry points for operator environment checks,
36. Phase 3 shared retry/backoff support for transient WordPress and Facebook transport failures,
37. Phase 3 operator-facing schedule planning reporting for queue-ready, scheduled, and collision-heavy publish chains,
38. Phase 4 on-demand publish-chain snapshots derived from source, draft, review, publish, queue, and mapping records,
39. Phase 4 operator-facing publish-chain history reporting from the current append-only runtime baseline,
40. Phase 4 dedicated exception, activity, and variant-usage tracking views built on the same normalized chain snapshot,
41. Phase 4 append-only tracking audit records for deliberate normalization runs and execute-mode transport validation,
42. a locked Phase 4 policy to keep normalized publish-chain snapshots on demand until real Phase 5 or operator-pressure triggers justify persistence,
43. a focused cross-phase smoke test that proves one clean chain can move from Source Engine through Tracking Foundation without hidden contract breaks,
44. CLI entry points for intake, draft creation, review, reporting, reset, micro-skill application, gold-set replay, local WordPress/Facebook/linkage preparation, transport validation, distribution-health reporting, distribution-schedule reporting, publish-chain history reporting, tracking-audit reporting, and WordPress/Facebook transport preview/execute flows,
45. explicit non-unique-source rejection in the Content Engine eligibility path so duplicate snapshots do not drift into draft formatting,
46. Phase 4.5 ignored local config scaffolding plus a recorded local pre-live canary-preparation chain that reaches WordPress preparation, social packaging, linkage refresh, distribution reporting, publish-chain normalization, and tracking audit without execute-mode remote transport.
47. an operator-facing system-activation readiness report that summarizes config placeholders, approved canary candidates, validation evidence, and the remaining live activation blockers in one place,
48. a safe WordPress remote-state inspection and append-only local reconciliation path for live canaries after manual WordPress admin actions,
49. a real replacement canary chain with a published WordPress post, an append-only local reconciliation snapshot, and a recorded Facebook publish failure caused by an expired Page token rather than missing system behavior,
50. append-only queue review records for operator queue approval and schedule gating,
51. an internal operator API for dashboard, draft review, social review, media review, queue review, queue scheduling, and combined health,
52. a thin WordPress admin plugin shell for dashboard, draft review, social review, media review, queue review, and settings,
53. an approval UI runbook and acceptance evidence for the first operator-console baseline,
54. operator-facing dashboard activity and alert visibility so the approval console shows what changed and what is currently blocked,
55. an explicit queue-removal path so the operator can pull an item out of the current batch without faking another review outcome,
56. richer detail-screen context so the operator can see source lineage and downstream linkage without leaving the approval shell,
57. explicit queue-approval block reasons so failed queue items do not present false approve actions in the UI,
58. dashboard activity and alert navigation so the operator can jump directly into the relevant review detail screen when the backend can resolve a safe target,
59. a dedicated approval-UI Validation page backed by one operator-readiness endpoint so live WordPress-admin verification can start from a clear baseline instead of ad hoc checks,
60. a defined runtime policy for the operator API so future WordPress-admin use does not depend on ad hoc terminal commands or impossible localhost assumptions across separate hosts,
61. plugin-side Operator API reachability guidance plus reverse-proxy deployment examples so hosted WordPress validation has a concrete path instead of a vague warning,
62. a Coolify-ready Operator API container baseline with health endpoint, env-driven runtime config, and Git-autodeploy runbook,
63. an optional OpenAI provider layer using the official SDK and Responses API behind the existing draft micro-skill seam,
64. explicit `--provider openai` support for draft micro-skills with bounded retry, heuristic fallback, and non-secret fallback reporting,
65. a manual `refine_social_package.py` flow that appends review-safe OpenAI Facebook package variants without changing the selected package or approval state,
66. review-visible AI provenance on draft and social package records surfaced through the operator API and approval UI detail screens,
67. runtime backup and restore CLIs for `data/` and optional `config/*.local.json`,
68. example `systemd` services and timers for intake, daily reports, and runtime backups on the production worker host,
69. a Phase 4.7 media engine with append-only media brief, asset, and asset-review records,
70. manual media CLIs for creating media briefs, registering provenance-tagged assets, and recording operator asset reviews,
71. asset-readiness visibility in distribution health, operator API detail payloads, the WordPress approval shell, queue context, and validation reporting,
72. publish-chain-safe asset completeness metadata so blog and Facebook outputs can see whether a reviewed asset is actually attached.

The main code currently lives in:

1. [src/source_engine](C:/Users/Administrator/OneDrive/Documents/co_ma/src/source_engine)
2. [src/content_engine](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine)
3. [src/distribution_engine](C:/Users/Administrator/OneDrive/Documents/co_ma/src/distribution_engine)
4. [src/content_engine/taxonomy.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/taxonomy.py)
5. [src/content_engine/micro_skills.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/micro_skills.py)
6. [src/content_engine/health.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/health.py)
7. [src/content_engine/routing.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/routing.py)
8. [src/content_engine/formatting_cli.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/formatting_cli.py)
9. [src/content_engine/health_cli.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/health_cli.py)
10. [src/cli/run_source_intake.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/run_source_intake.py)
11. [src/cli/review_source_status.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/review_source_status.py)
12. [src/cli/create_draft_from_source_item.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/create_draft_from_source_item.py)
13. [src/cli/review_draft.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/review_draft.py)
14. [src/cli/apply_draft_micro_skills.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/apply_draft_micro_skills.py)
15. [src/cli/prepare_wordpress_publish.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/prepare_wordpress_publish.py)
16. [src/cli/prepare_facebook_package.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/prepare_facebook_package.py)
17. [src/cli/prepare_distribution_linkage.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/prepare_distribution_linkage.py)
18. [src/cli/review_social_package.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/review_social_package.py)
19. [src/cli/record_wordpress_publish_update.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/record_wordpress_publish_update.py)
20. [src/distribution_engine/wordpress_transport.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/distribution_engine/wordpress_transport.py)
21. [src/distribution_engine/wordpress_transport_cli.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/distribution_engine/wordpress_transport_cli.py)
22. [src/cli/sync_wordpress_transport.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/sync_wordpress_transport.py)
23. [src/distribution_engine/facebook_transport.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/distribution_engine/facebook_transport.py)
24. [src/distribution_engine/facebook_transport_cli.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/distribution_engine/facebook_transport_cli.py)
25. [src/cli/sync_facebook_transport.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/sync_facebook_transport.py)
26. [src/cli/summarize_source_health.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/summarize_source_health.py)
27. [src/cli/summarize_draft_health.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/summarize_draft_health.py)
28. [src/cli/summarize_publish_chain_history.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/summarize_publish_chain_history.py)
29. [src/cli/summarize_tracking_audit.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/summarize_tracking_audit.py)
30. [src/cli/reset_runtime_state.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/reset_runtime_state.py)
31. [src/operator_api](C:/Users/Administrator/OneDrive/Documents/co_ma/src/operator_api)
32. [src/cli/run_operator_api.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/cli/run_operator_api.py)
33. [src/ai_layer](C:/Users/Administrator/OneDrive/Documents/co_ma/src/ai_layer)
34. [src/tracking_engine](C:/Users/Administrator/OneDrive/Documents/co_ma/src/tracking_engine)
35. [wordpress-plugin/content-ops-approval-ui](C:/Users/Administrator/OneDrive/Documents/co_ma/wordpress-plugin/content-ops-approval-ui)
36. [data/source_registry.json](C:/Users/Administrator/OneDrive/Documents/co_ma/data/source_registry.json)

The current validation commands are:

```powershell
python -m unittest discover -s tests -v
python -m unittest tests.integration.test_phase1_to_phase4_chain -v
python src\cli\run_source_intake.py --limit-per-source 5
python src\cli\run_source_intake.py --limit-per-source 2 --fetch-article-bodies
python src\cli\review_source_status.py --source-id src_food_republic --reviewed-items 4 --strong-candidates 2 --weak-or-repetitive-items 1
python src\cli\create_draft_from_source_item.py --source-item-id <source_item_id>
python src\cli\review_draft.py --draft-id <draft_id> --outcome needs_edits --note "derivative_risk_fix: tighten wording"
python src\cli\apply_draft_micro_skills.py --draft-id <draft_id> --skill generate_headline_variants --skill generate_excerpt
python src\cli\apply_draft_micro_skills.py --draft-id <draft_id> --skill generate_headline_variants --skill generate_short_intro --skill generate_excerpt --provider openai --openai-config-path <openai_provider_config.local.json>
python src\cli\create_runtime_backup.py --backup-root <backup_dir>
python src\cli\prepare_wordpress_publish.py --draft-id <draft_id> --publish-intent draft
python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path <wordpress_rest_config.json>
python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path <wordpress_rest_config.json> --execute
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id <blog_publish_id> --config-path <wordpress_rest_config.json> --execute
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id <blog_publish_id> --config-path <wordpress_rest_config.json> --execute --reconcile-local-state
python src\cli\validate_wordpress_transport.py --config-path <wordpress_rest_config.json>
python src\cli\validate_wordpress_transport.py --config-path <wordpress_rest_config.json> --execute
python src\cli\validate_wordpress_transport.py --config-path <wordpress_rest_config.json> --execute --record-audit
python src\cli\prepare_facebook_package.py --draft-id <draft_id> --blog-publish-id <blog_publish_id>
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action published --config-path <facebook_graph_config.json>
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action scheduled --scheduled-for-facebook <timestamp> --schedule-mode manual --config-path <facebook_graph_config.json> --execute
python src\cli\validate_facebook_transport.py --config-path <facebook_graph_config.json>
python src\cli\validate_facebook_transport.py --config-path <facebook_graph_config.json> --execute
python src\cli\validate_facebook_transport.py --config-path <facebook_graph_config.json> --execute --record-audit
python src\cli\prepare_distribution_linkage.py --blog-publish-id <blog_publish_id> --social-package-id <social_package_id>
python src\cli\review_social_package.py --social-package-id <social_package_id> --outcome approved --note "hook_matches_blog"
python src\cli\refine_social_package.py --social-package-id <social_package_id> --provider openai --openai-config-path <openai_provider_config.local.json>
python src\cli\summarize_distribution_health.py
python src\cli\summarize_distribution_schedule.py
python src\cli\record_wordpress_publish_update.py --blog-publish-id <blog_publish_id> --action draft_created --wordpress-post-id <post_id> --wordpress-post-url <post_url>
python src\cli\record_wordpress_publish_update.py --blog-publish-id <blog_publish_id> --action scheduled --wordpress-post-id <post_id> --schedule-mode manual --scheduled-for-blog <timestamp>
python src\cli\record_facebook_publish_update.py --social-package-id <social_package_id> --action scheduled --facebook-post-id <facebook_post_id> --schedule-mode manual --scheduled-for-facebook <timestamp>
python src\cli\replay_phase2_gold_set.py
python src\cli\summarize_distribution_health.py --json
python src\cli\summarize_distribution_schedule.py --json
python src\cli\summarize_publish_chain_history.py
python src\cli\summarize_publish_chain_history.py --json
python src\cli\summarize_publish_chain_history.py --view exceptions --json
python src\cli\summarize_publish_chain_history.py --view activity --json
python src\cli\summarize_publish_chain_history.py --view variants --json
python src\cli\summarize_publish_chain_history.py --view all --json
python src\cli\summarize_publish_chain_history.py --view all --record-audit
python src\cli\summarize_tracking_audit.py
python src\cli\summarize_tracking_audit.py --json
python src\cli\summarize_source_health.py
python src\cli\summarize_draft_health.py
python src\cli\reset_runtime_state.py
python src\cli\restore_runtime_backup.py --backup-path <backup_zip> --target-root <restore_root> --dry-run
python src\cli\run_operator_api.py
powershell -ExecutionPolicy Bypass -File scripts\run_operator_api.ps1
```

For live operator activation, the recommended local config examples now live in:

1. [config/README.md](C:/Users/Administrator/OneDrive/Documents/co_ma/config/README.md)
2. [config/wordpress_rest_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/wordpress_rest_config.example.json)
3. [config/facebook_graph_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/facebook_graph_config.example.json)
4. [config/openai_provider_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/openai_provider_config.example.json)
5. [config/operator_api_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/operator_api_config.example.json)
6. [scripts/run_operator_api.ps1](C:/Users/Administrator/OneDrive/Documents/co_ma/scripts/run_operator_api.ps1)
7. [deploy/systemd/content-ops-operator-api.service.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-operator-api.service.example)

The runtime data files and how to treat them are documented in [data/README.md](C:/Users/Administrator/OneDrive/Documents/co_ma/data/README.md).

The current test baseline is `python -m unittest discover -s tests -v`, which now covers Source Engine, the implemented Phase 2 Content Engine slices, the current Phase 3 distribution slices, and the current Phase 4 tracking slices for on-demand publish-chain history plus exception, activity, variant, and tracking-audit reporting. It also now includes a focused cross-phase smoke test from source item through tracking audit, the Phase 4.5 system-activation readiness-reporting slice, the WordPress remote-state reconciliation slice, the optional Phase 4.6 OpenAI quality layer with safe fallback behavior and manual social refinement, the Phase 4.7 media brief and asset-review flow, the operator API slice, queue-review behavior, dashboard activity and alert visibility, explicit queue-removal handling, queue-approval block guidance, dashboard-to-detail navigation hints, the operator-validation endpoint for live plugin readiness, the review-speed layer for filtered inboxes, priority dashboard queues, safe variant-selection actions, read-only AI provenance visibility, and the Phase 4.8 runtime backup and restore tooling baseline. The current green baseline is `253` tests passing, and that baseline is maintained through the repo test suite rather than hand-waved phase notes.

## Repository Intent

This repository should remain understandable by one person. Every new file should make execution clearer, not more abstract.
