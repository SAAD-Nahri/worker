# TODO

This is the master execution checklist for the project. It should be updated as work progresses. The goal is to keep execution grounded, phased, and visible.

## Rules For This List

1. only add tasks that clearly support the current phase,
2. do not add future-phase work unless it affects current planning,
3. do not convert this file into a brainstorm dump,
4. use this file to create momentum, not noise.

## Phase 0: Foundation and Planning

### Completed

- [x] Create the master plan.
- [x] Create the project README and navigation docs.
- [x] Create locked-decision documentation.
- [x] Create phase documentation.
- [x] Create standard phase-governance, closeout, and entry templates so every phase can end cleanly.
- [x] Create an open-questions list.
- [x] Create phase-specific planning briefs.
- [x] Confirm the first source selection criteria for food-facts content.
- [x] Define the initial source registry fields.
- [x] Decide how source families will be categorized.
- [x] Define the first version of the content-state lifecycle in implementation terms.
- [x] Define the minimum dedupe requirements for sourced items.
- [x] Define the first blog template set for the niche.
- [x] Define the first Facebook packaging template set.
- [x] Define what must be manually approved before publishing.
- [x] Decide the minimum viable publish history fields.
- [x] Choose the initial implementation target for the Source Engine.
- [x] Decide where the first source registry records will live operationally.
- [x] Decide where workflow state and publish history records will live operationally.
- [x] Confirm the smallest viable review loop for v1 execution.
- [x] Select the first real source domains for the food-facts niche.
- [x] Confirm the first 5 to 10 sources to seed the registry.
- [x] Decide the first manual source-review workflow for intake.
- [x] Define the first pilot operating plan.
- [x] Decide the day-one active source registry.
- [x] Decide the week-one family emphasis and intake targets.
- [x] Define the week-one intake operating plan.
- [x] Create the first working intake log template.
- [x] Create the first working shortlist log template.
- [x] Create the first live intake log.
- [x] Create the first live shortlist log.
- [x] Convert the active registry into the first implementation-ready registry format.
- [x] Start recording candidate items in the live intake log.
- [x] Start recording advanced items in the live shortlist log.

### Still needed before Phase 1 starts

- [x] Begin implementing the Source Engine against the active registry and specs.

## Phase 1: Source Engine

- [x] Implement the source registry schema in the application.
- [x] Implement the RSS intake workflow.
- [x] Implement selective scraping boundaries and fallback handling.
- [x] Implement the normalized source item model.
- [x] Implement cleaner behavior for raw source items.
- [x] Implement classifier behavior for source items.
- [x] Implement dedupe checks for source items.
- [x] Implement source audit logging.
- [x] Load the first active source batch into the application-facing registry.
- [x] Implement source status validation and intake gating.
- [x] Implement opt-in article-body fetch logic for unique items that need more than feed summaries.
- [x] Implement review-driven source keep, downgrade, pause, and retire decision recording.
- [x] Lock the Phase 1 article-body rule: keep it as an opt-in intake-time path for unique items, not a default or a broad crawler.
- [x] Implement source health reporting for operator review.
- [x] Implement an explicit archive-first clean-run reset workflow while keeping append-only logging as the default.
- [x] Lock the Phase 1 source-review rule: registry updates remain operator-applied, not automatic by default.
- [x] Implement cleaner fallback rules for non-RSS or degraded sources.

## Phase 2: Content Engine

- [x] Define the draft record shape for Content Engine outputs.
- [x] Define the first blog template contracts with concrete section order and target length ranges.
- [x] Define the first-pass content quality gate policy.
- [x] Define the v1 derivative-risk policy.
- [x] Define the allowed AI micro-skill policy for Content Engine use.
- [x] Define the v1 category and tag policy.
- [x] Define the deterministic content formatting pipeline.
- [x] Define the draft review workflow.
- [x] Define the Phase 2 execution plan and validation plan.
- [x] Implement draft record model and append-only draft storage foundations.
- [x] Implement blog template contracts in the application.
- [x] Harden the template layer with executable slot-level guidance, bullet-count rules, and early-answer enforcement for the accepted v1 contracts.
- [x] Implement formatting engine inputs and outputs.
- [x] Implement quality checks for readability, structure, and derivative risk.
- [x] Implement an operator-facing draft creation entry point for Phase 2 execution.
- [x] Implement operator-facing draft health reporting for review readiness and handoff visibility.
- [x] Implement the first bounded micro-skill baseline for headline variants, intro tightening, and excerpt refinement.
- [x] Run the first live Phase 2 acceptance batch and record before/after draft-health findings.
- [x] Implement the bounded Phase 2 micro-skill baseline and define its exact allowed-role policy.
- [x] Improve topic-term extraction so low-signal tokens do not drive intros and section phrasing.
- [x] Add semantic coherence checks that catch awkward term lists before manual review.
- [x] Add deterministic content-fit signals for recipe-heavy and noisy source context.
- [x] Record a second live-style Phase 2 acceptance replay focused on anchor-quality improvements.
- [x] Build the fixed Phase 2 gold-set acceptance pack baseline and replay harness.
- [x] Decide the first weak-fit source routing rules for reroute, hold, review-only, and reject behavior.
- [x] Make routing recommendations visible in the operator draft-health reporting path.
- [x] Make the initial routing recommendation visible at draft-creation time as well as in batch reporting.
- [x] Record a routing-visible Phase 2 acceptance replay against current runtime draft state.
- [x] Expand the gold set with additional live weak-fit cases and replay it as closeout-oriented evidence.
- [x] Define the explicit Phase 2 closeout checklist so remaining work is judged against clear gates.
- [x] Add the first live blocked case to the fixed gold set and replay it as closeout evidence.
- [x] Improve bounded headline-variant generation so heuristic outputs are either cleaner or clearly labeled as scratch suggestions.
- [x] Harden post-review micro-skill behavior so content-affecting intro rewrites refresh quality state and reopen review.
- [x] Harden explicit template override handling so operators cannot force a source item across template families.
- [x] Implement draft review requirements.
- [x] Implement article categories and tagging rules.
- [x] Preserve required source-item lineage into the draft record.
- [x] Audit remaining Phase 2 scope and separate deferred follow-up work from real closeout blockers.
- [x] Create the Phase 3 entry checklist before Phase 2 closeout.
- [x] Decide whether the fixed gold set needs one more clean-fit expansion before Phase 2 closeout.
- [x] Write the formal Phase 2 closeout review once the remaining closeout decision is settled.

## Phase 3: Social Packaging + Distribution

- [x] Define the first WordPress publishing contract.
- [x] Define the first Facebook packaging template contracts.
- [x] Define the distribution queue-state model.
- [x] Define the blog-to-Facebook mapping contract.
- [x] Define the Phase 3 execution plan and validation plan.
- [x] Implement the first approved-draft-to-WordPress payload baseline with deterministic HTML rendering and append-only local publish records.
- [x] Implement Facebook hook template families.
- [x] Implement caption template families.
- [x] Implement comment CTA template families.
- [x] Implement the first approved-draft-to-Facebook package baseline with deterministic packaging derivation, explicit blog-link handling, and append-only local social package records.
- [x] Implement the initial queue-record baseline for blog review readiness, social packaging pending, and social queue readiness.
- [x] Implement the initial blog-to-Facebook mapping record baseline with preserved selected output values.
- [x] Implement the initial manual social-package review workflow with append-only review logging.
- [x] Implement the initial local WordPress publish-state update workflow with refreshed queue and mapping snapshots.
- [x] Implement queue state transitions for scheduling and publish/failure updates.
- [x] Implement Facebook post publish identifiers and final mapping-state updates.
- [x] Implement scheduling rules for auto-scheduled versus manually approved content.
- [x] Choose WordPress REST with application-password auth as the first real WordPress transport.
- [x] Implement a dry-run-safe WordPress REST draft-sync adapter with append-only success and failure recording.
- [x] Choose the first Facebook posting or scheduling transport.
- [x] Implement the first Facebook transport adapter with the same dry-run-safe, append-only pattern used for WordPress.
- [x] Implement operator-facing distribution health reporting from Phase 3 runtime records.
- [x] Surface schedule collisions and broken-chain consistency issues in the distribution-health layer.
- [x] Create the first Phase 3 distribution runbook so publishing, packaging, transport, and health review use one operator path.
- [x] Implement non-mutating WordPress transport validation for operator config checks.
- [x] Implement non-mutating Facebook transport validation for operator config checks.
- [x] Implement shared retry/backoff support for transient WordPress and Facebook transport failures.
- [x] Implement operator-facing distribution schedule planning reporting.
- [x] Separate true Phase 3 residual items from closeout blockers.
- [x] Write the formal Phase 3 closeout review.
- [x] Create the Phase 4 entry checklist before Phase 3 handoff.

## Phase 4: Tracking Foundation

- [x] Define the first normalized publish-chain snapshot contract.
- [x] Define publish history normalization rules grounded in the current append-only runtime records.
- [x] Define stable lineage join rules from source item to Facebook publish.
- [x] Define the first variant recording rules for the tracking layer.
- [x] Define the Phase 4 tracking log policy.
- [x] Define the first reporting views for Phase 4.
- [x] Define the Phase 4 execution plan and validation plan.
- [x] Implement the first on-demand publish-chain snapshot and ledger reporting baseline.
- [x] Implement the first deterministic source-to-blog-to-Facebook lineage join layer on top of current runtime records.
- [x] Implement the first selected-value variant normalization and reporting baseline.
- [x] Implement the minimum operator reporting views for exceptions, activity mix, and variant usage.
- [x] Confirm the current Phase 4 default: keep normalized chain snapshots derived on demand first instead of persisting a second runtime artifact.
- [x] Implement operational logs needed for debugging and audits.
- [x] Decide when normalized publish-chain snapshots should become a persisted runtime artifact instead of remaining on-demand.
- [x] Add a focused cross-phase smoke test that proves one clean chain can move from source item through tracking and audit.
- [x] Separate true Phase 4 residual items from closeout blockers.
- [x] Write the formal Phase 4 closeout review.
- [x] Create the Phase 5 entry checklist before Phase 4 handoff.

## Phase 4.5: System Activation And Live Validation

- [x] Define the Phase 4.5 activation objective and boundary.
- [x] Define the local secrets and transport-config policy.
- [x] Define the Phase 4.5 execution plan and validation plan.
- [x] Create safe example config files for WordPress and Facebook local setup.
- [x] Create the system activation runbook.
- [x] Create operator-local WordPress and Facebook config scaffolding files in ignored `.local.json` paths.
- [x] Implement operator-facing system-activation readiness reporting.
- [x] Add the real WordPress application password, taxonomy mappings, and base URL to the local config.
- [x] Add the real Facebook Page id and Page access token to the local config.
- [x] Run dry-run validation for both transports using the local config scaffolding files.
- [x] Run execute-mode validation with audit recording for both transports.
- [x] Select one technical canary draft for the local pre-live activation path.
- [x] Run one controlled local canary-preparation chain through draft approval, WordPress preparation, social packaging, and linkage.
- [x] Review distribution health, schedule, and publish-chain history after the local canary-preparation flow.
- [x] Record the first Phase 4.5 activation acceptance batch.
- [x] Implement safe WordPress remote-state inspection and append-only local reconciliation for live canaries.
- [x] Reconcile the replacement canary from the real remote WordPress published state.
- [x] Attempt the first live Facebook canary publish against the owned Page.
- [ ] Refresh the expired Facebook Page access token in the local config.
- [ ] Rerun execute-mode Facebook validation with audit recording after token refresh.
- [ ] Retry the replacement-canary Facebook publish after token refresh.
- [ ] Write the formal Phase 4.5 closeout review.

## Phase 4.6: AI-Assisted Content Quality

- [x] Define the provider-backed micro-skill architecture.
- [x] Define the first provider credential policy for optional local AI usage.
- [x] Define the prompt and output contracts for provider-backed headline, intro, and excerpt skills.
- [x] Preserve deterministic and heuristic fallback behavior as a hard rule.
- [x] Implement the first optional provider-backed quality skills.
- [x] Validate quality gains without allowing full-article generation.
- [x] Record the first acceptance batch for AI-assisted content quality.

## Phase 4.7: Media And Asset Layer

- [x] Define the media and visual-asset policy.
- [x] Define the first media record and linkage model.
- [x] Define the first media brief contract from approved draft context.
- [x] Decide the first allowed media source type for the baseline.
- [x] Implement the first operator-reviewed media flow for blog and Facebook outputs.
- [x] Preserve asset provenance, review state, and linkage in the publish chain.
- [x] Record the first acceptance batch for media and asset handling.

## Phase 4.8: Runtime Operations And Deployment

- [x] Define the recommended runtime operating model for the finished system.
- [x] Define the first deployment and scheduling policy for solo-operator production use.
- [x] Define the first backup and recovery policy.
- [x] Define the Phase 4.8 execution plan and validation plan.
- [x] Create the operations and deployment runbook.
- [x] Define the operator API runtime policy for local development and future production hosting.
- [x] Implement the first production-host deployment baseline for the chosen runtime target.
- [ ] Rehearse a cold-start deployment on the chosen host.
- [ ] Rehearse a backup and recovery drill against real runtime data.
- [ ] Write the formal Phase 4.8 closeout review.

## Phase 4.9: Approval UI And Operator Console

- [x] Define the approval UI contract so human review has a clear place in the system.
- [x] Define the operator API contract.
- [x] Define the WordPress admin approval-plugin contract.
- [x] Define the Phase 4.9 execution plan and validation plan.
- [x] Implement append-only queue review records for operator queue approval.
- [x] Implement the first internal operator API on top of runtime records and review/update actions.
- [x] Implement the first WordPress admin approval plugin shell.
- [x] Expose queue schedule eligibility explicitly so the approval UI can show blocked scheduling reasons before submit.
- [x] Surface recent review activity and current alert signals on the approval dashboard.
- [x] Support explicit queue removal from the current batch as a first-class audited review outcome.
- [x] Surface richer source, draft, and mapping context on the approval detail screens.
- [x] Surface explicit queue-approval block reasons so failed queue items do not present false approve actions.
- [x] Make dashboard recent activity and resolvable alerts link directly into the relevant review detail screens.
- [x] Add dedicated live-validation support in the operator API and WordPress admin plugin.
- [x] Create the operator approval UI runbook.
- [x] Record the first Approval UI acceptance batch for the backend and plugin-shell baseline.
- [x] Record the queue-guidance hardening batch for Phase 4.9.
- [x] Record the dashboard hardening batch for Phase 4.9.
- [x] Record the queue-removal hardening batch for Phase 4.9.
- [x] Record the detail-context hardening batch for Phase 4.9.
- [x] Record the queue-actionability and dashboard-navigation hardening batch for Phase 4.9.
- [x] Record the live-validation support batch for Phase 4.9.
- [x] Add plugin-side operator-API reachability guidance for same-host versus hosted-WordPress deployments.
- [x] Add reverse-proxy deployment examples for the operator API.
- [x] Add a Coolify-ready Operator API container baseline.
- [x] Add a hosted Coolify deployment runbook with Git autodeploy guidance.
- [x] Add dashboard priority review-now sections for drafts, social packages, and queue items.
- [x] Add inbox filtering and search across draft, social, and queue review surfaces.
- [x] Add inline quick approve and quick needs-edits review actions for daily triage.
- [x] Add bounded headline-variant and social-variant selection on detail screens.
- [x] Add a dedicated media-review surface to the WordPress approval shell with linked asset context.
- [x] Add focused backend regression coverage for filtering, priority queues, and variant selection.
- [ ] Validate the plugin in a real WordPress admin environment.
- [ ] Record the first live plugin validation batch.
- [ ] Write the formal Phase 4.9 closeout review.

## Phase 5: Decision Layer

- [ ] Do not begin Phase 5 implementation until Phases 4.5, 4.6, 4.7, 4.8, and 4.9 are complete.
- [ ] Implement early winner signals.
- [ ] Implement source scoring factors.
- [ ] Implement template and hook comparison metrics.
- [ ] Implement promotion candidate rules.
- [ ] Confirm what intelligence can remain deterministic before any advanced reasoning layer is considered.
- [ ] Revisit persisted normalized snapshot storage only if Phase 5 needs frozen comparison cohorts or on-demand normalization becomes materially painful.

## Phase 5.5: Approval Automation And Autopilot

- [ ] Do not begin Phase 5.5 implementation until Phase 5 scoring and guardrails are complete.
- [ ] Define the first autoapproval and autopilot policy.
- [ ] Define shadow-mode scoring and approval logging rules.
- [ ] Define narrow eligibility lanes for automatic approval.
- [ ] Define operator override, rollback, and kill-switch rules.
- [ ] Validate false-positive tolerance before any live autoapproval lane is enabled.
- [ ] Record the first acceptance batch for approval automation.

## Phase 6: Scaling Layer

- [ ] Implement the conditions under which paid amplification becomes valid.
- [ ] Implement the conditions under which source expansion becomes justified.
- [ ] Implement the conditions under which channel expansion becomes justified.
- [ ] Implement the conditions under which OpenClaw or role-based orchestration becomes worth adding.

## Important Do-Not-Do Items

- [ ] Do not start with full AI article generation.
- [ ] Do not add OpenClaw as a foundation dependency.
- [ ] Do not expand to groups, multilingual, or paid traffic before the core loop is stable.
- [ ] Do not build a custom blog platform.
- [ ] Do not treat Facebook packaging as a minor output.

## Planning Assets Created

- [x] `MASTER_PLAN.md`
- [x] `LOCKED_DECISIONS.md`
- [x] `PHASES.md`
- [x] `OPEN_QUESTIONS.md`
- [x] `docs/phases/PHASE_GOVERNANCE.md`
- [x] `docs/phases/PHASE_CLOSEOUT_TEMPLATE.md`
- [x] `docs/phases/PHASE_ENTRY_TEMPLATE.md`
- [x] `docs/specs/SOURCE_REGISTRY_SPEC.md`
- [x] `docs/specs/WORKFLOW_STATE_MODEL.md`
- [x] `docs/specs/DEDUPE_POLICY.md`
- [x] `docs/specs/TEMPLATE_LIBRARY_V1.md`
- [x] `docs/specs/DRAFT_RECORD_SPEC.md`
- [x] `docs/specs/BLOG_TEMPLATE_CONTRACTS_V1.md`
- [x] `docs/specs/CONTENT_QUALITY_GATES.md`
- [x] `docs/specs/DERIVATIVE_RISK_POLICY.md`
- [x] `docs/specs/AI_MICRO_SKILL_POLICY.md`
- [x] `docs/specs/CATEGORY_AND_TAG_POLICY_V1.md`
- [x] `docs/specs/CONTENT_FORMATTING_PIPELINE_V1.md`
- [x] `docs/specs/CONTENT_FIT_GATE_V1.md`
- [x] `docs/specs/WEAK_FIT_ROUTING_POLICY_V1.md`
- [x] `docs/specs/DRAFT_REVIEW_WORKFLOW_V1.md`
- [x] `docs/specs/DRAFT_HEALTH_REPORTING_V1.md`
- [x] `docs/specs/PUBLISH_HISTORY_SCHEMA.md`
- [x] `docs/specs/APPROVAL_WORKFLOW.md`
- [x] `docs/specs/V1_IMPLEMENTATION_TARGET.md`
- [x] `docs/specs/WORDPRESS_PUBLISHING_CONTRACT_V1.md`
- [x] `docs/specs/FACEBOOK_GRAPH_TRANSPORT_V1.md`
- [x] `docs/specs/WORDPRESS_REST_TRANSPORT_V1.md`
- [x] `docs/specs/WORDPRESS_TRANSPORT_VALIDATION_V1.md`
- [x] `docs/specs/FACEBOOK_TRANSPORT_VALIDATION_V1.md`
- [x] `docs/specs/FACEBOOK_PACKAGING_TEMPLATE_CONTRACTS_V1.md`
- [x] `docs/specs/DISTRIBUTION_QUEUE_MODEL_V1.md`
- [x] `docs/specs/BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md`
- [x] `docs/specs/DISTRIBUTION_HEALTH_REPORTING_V1.md`
- [x] `docs/specs/DISTRIBUTION_SCHEDULE_REPORTING_V1.md`
- [x] `docs/specs/PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md`
- [x] `docs/specs/PUBLISH_HISTORY_NORMALIZATION_V1.md`
- [x] `docs/specs/TRACKING_LINEAGE_JOIN_RULES_V1.md`
- [x] `docs/specs/VARIANT_RECORDING_RULES_V1.md`
- [x] `docs/specs/TRACKING_LOG_POLICY_V1.md`
- [x] `docs/specs/TRACKING_REPORTING_VIEWS_V1.md`
- [x] `docs/specs/TRACKING_AUDIT_RECORDS_V1.md`
- [x] `docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md`
- [x] `docs/phases/PHASE_2_CLOSEOUT_CHECKLIST.md`
- [x] `docs/phases/PHASE_2_CLOSEOUT.md`
- [x] `docs/phases/PHASE_2_RESIDUAL_ITEMS.md`
- [x] `docs/phases/PHASE_3_ENTRY_CHECKLIST.md`
- [x] `docs/phases/PHASE_3_EXECUTION_PLAN.md`
- [x] `docs/phases/PHASE_3_VALIDATION_PLAN.md`
- [x] `docs/phases/PHASE_3_CLOSEOUT_CHECKLIST.md`
- [x] `docs/phases/PHASE_3_CLOSEOUT.md`
- [x] `docs/phases/PHASE_3_RESIDUAL_ITEMS.md`
- [x] `docs/phases/PHASE_4_ENTRY_CHECKLIST.md`
- [x] `docs/phases/PHASE_4_EXECUTION_PLAN.md`
- [x] `docs/phases/PHASE_4_VALIDATION_PLAN.md`
- [x] `docs/phases/PHASE_4_CLOSEOUT_CHECKLIST.md`
- [x] `docs/phases/PHASE_4_RESIDUAL_ITEMS.md`
- [x] `docs/phases/PHASE_4_CLOSEOUT.md`
- [x] `docs/phases/PHASE_5_ENTRY_CHECKLIST.md`
- [x] `docs/phases/PHASE_4_5_SYSTEM_ACTIVATION.md`
- [x] `docs/phases/PHASE_4_5_ENTRY_CHECKLIST.md`
- [x] `docs/phases/PHASE_4_5_EXECUTION_PLAN.md`
- [x] `docs/phases/PHASE_4_5_VALIDATION_PLAN.md`
- [x] `docs/phases/PHASE_4_6_AI_ASSISTED_CONTENT_QUALITY.md`
- [x] `docs/phases/PHASE_4_6_EXECUTION_PLAN.md`
- [x] `docs/phases/PHASE_4_6_VALIDATION_PLAN.md`
- [x] `docs/phases/PHASE_4_7_MEDIA_AND_ASSET_LAYER.md`
- [x] `docs/phases/PHASE_4_7_EXECUTION_PLAN.md`
- [x] `docs/phases/PHASE_4_7_VALIDATION_PLAN.md`
- [x] `docs/phases/PHASE_4_8_RUNTIME_OPERATIONS_AND_DEPLOYMENT.md`
- [x] `docs/phases/PHASE_4_8_EXECUTION_PLAN.md`
- [x] `docs/phases/PHASE_4_8_VALIDATION_PLAN.md`
- [x] `docs/phases/PHASE_4_9_APPROVAL_UI_AND_OPERATOR_CONSOLE.md`
- [x] `docs/phases/PHASE_4_9_EXECUTION_PLAN.md`
- [x] `docs/phases/PHASE_4_9_VALIDATION_PLAN.md`
- [x] `docs/phases/PHASE_5_5_APPROVAL_AUTOMATION_AND_AUTOPILOT.md`
- [x] `docs/phases/PHASE_5_5_EXECUTION_PLAN.md`
- [x] `docs/phases/PHASE_5_5_VALIDATION_PLAN.md`
- [x] `docs/specs/LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md`
- [x] `docs/specs/AI_ASSISTED_CONTENT_QUALITY_POLICY_V1.md`
- [x] `docs/specs/MEDIA_AND_VISUAL_ASSET_POLICY_V1.md`
- [x] `docs/specs/OPENAI_PROVIDER_CONFIG_POLICY_V1.md`
- [x] `docs/specs/AI_MICRO_SKILL_PROMPT_CONTRACTS_V1.md`
- [x] `docs/specs/MEDIA_BRIEF_CONTRACT_V1.md`
- [x] `docs/specs/ASSET_RECORD_AND_LINKAGE_CONTRACT_V1.md`
- [x] `docs/specs/APPROVAL_UI_CONTRACT_V1.md`
- [x] `docs/specs/OPERATOR_API_CONTRACT_V1.md`
- [x] `docs/specs/WORDPRESS_ADMIN_APPROVAL_PLUGIN_V1.md`
- [x] `docs/specs/RUNTIME_OPERATING_MODEL_V1.md`
- [x] `docs/specs/OPERATOR_API_RUNTIME_POLICY_V1.md`
- [x] `docs/specs/DEPLOYMENT_AND_SCHEDULING_POLICY_V1.md`
- [x] `docs/specs/BACKUP_AND_RECOVERY_POLICY_V1.md`
- [x] `docs/specs/AUTOAPPROVAL_AND_AUTOPILOT_POLICY_V1.md`
- [x] `docs/specs/SYSTEM_ACTIVATION_READINESS_REPORTING_V1.md`
- [x] `docs/execution/SYSTEM_ACTIVATION_RUNBOOK.md`
- [x] `docs/execution/OPERATIONS_AND_DEPLOYMENT_RUNBOOK.md`
- [x] `docs/execution/APPROVAL_UI_RUNBOOK.md`
- [x] `config/README.md`
- [x] `config/wordpress_rest_config.example.json`
- [x] `config/facebook_graph_config.example.json`
- [x] `config/openai_provider_config.example.json`
- [x] `config/operator_api_config.example.json`
- [x] `docs/phases/PHASE_2_EXECUTION_PLAN.md`
- [x] `docs/phases/PHASE_2_VALIDATION_PLAN.md`
- [x] `docs/execution/SOURCE_CANDIDATES.md`
- [x] `docs/execution/ACTIVE_SOURCE_REGISTRY_V1.md`
- [x] `docs/execution/ACTIVE_SOURCE_REGISTRY_RECORDS_V1.md`
- [x] `docs/execution/SOURCE_REVIEW_CHECKLIST.md`
- [x] `docs/execution/WEEK_1_INTAKE_PLAN.md`
- [x] `docs/execution/PILOT_PLAN.md`
- [x] `docs/execution/SOURCE_ENGINE_RUNBOOK.md`
- [x] `docs/execution/INTAKE_LOG_TEMPLATE.md`
- [x] `docs/execution/SHORTLIST_LOG_TEMPLATE.md`
- [x] `docs/execution/LIVE_INTAKE_LOG.md`
- [x] `docs/execution/LIVE_SHORTLIST_LOG.md`
- [x] `docs/execution/CONTENT_ENGINE_RUNBOOK.md`
- [x] `docs/execution/DISTRIBUTION_ENGINE_RUNBOOK.md`
- [x] `docs/execution/TRACKING_ENGINE_RUNBOOK.md`
- [x] `docs/execution/PHASE_2_ACCEPTANCE_BATCH_1.md`
- [x] `docs/execution/PHASE_2_ACCEPTANCE_BATCH_2.md`
- [x] `docs/execution/PHASE_2_ACCEPTANCE_BATCH_3.md`
- [x] `docs/execution/PHASE_2_ACCEPTANCE_BATCH_4.md`
- [x] `docs/execution/PHASE_2_ACCEPTANCE_BATCH_5.md`
- [x] `docs/execution/PHASE_2_ACCEPTANCE_BATCH_6.md`
- [x] `docs/execution/PHASE_2_ACCEPTANCE_BATCH_7.md`
- [x] `docs/execution/PHASE_2_ACCEPTANCE_BATCH_8.md`
- [x] `docs/execution/PHASE_2_ACCEPTANCE_BATCH_9.md`
- [x] `docs/execution/PHASE_3_ACCEPTANCE_BATCH_1.md`
- [x] `docs/execution/PHASE_3_ACCEPTANCE_BATCH_2.md`
- [x] `docs/execution/PHASE_3_ACCEPTANCE_BATCH_3.md`
- [x] `docs/execution/PHASE_3_ACCEPTANCE_BATCH_4.md`
- [x] `docs/execution/PHASE_3_ACCEPTANCE_BATCH_5.md`
- [x] `docs/execution/PHASE_3_ACCEPTANCE_BATCH_6.md`
- [x] `docs/execution/PHASE_3_ACCEPTANCE_BATCH_7.md`
- [x] `docs/execution/PHASE_3_ACCEPTANCE_BATCH_8.md`
- [x] `docs/execution/PHASE_3_ACCEPTANCE_BATCH_9.md`
- [x] `docs/execution/PHASE_4_ACCEPTANCE_BATCH_1.md`
- [x] `docs/execution/PHASE_4_ACCEPTANCE_BATCH_2.md`
- [x] `docs/execution/PHASE_4_ACCEPTANCE_BATCH_3.md`
- [x] `docs/execution/PHASE_4_ACCEPTANCE_BATCH_4.md`
- [x] `docs/execution/PHASE_4_ACCEPTANCE_BATCH_5.md`
- [x] `docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_1.md`
- [x] `docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_2.md`
- [x] `docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_3.md`
- [x] `docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_4.md`
- [x] `docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_5.md`
- [x] `docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_6.md`
- [x] `docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_1.md`
- [x] `docs/execution/PHASE_4_9_ACCEPTANCE_BATCH_2.md`
- [x] `docs/execution/PHASE_2_GOLD_SET_V1.md`
- [x] `docs/execution/PHASE_2_GOLD_SET_V1.json`
