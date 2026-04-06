# Phase 3: Social Packaging and Distribution

## Objective

Publish approved content to WordPress and derive Facebook-ready distribution assets from the blog draft.

## Why This Phase Matters

The business model depends on distribution, not just content creation. This phase turns the content engine into an actual traffic system by connecting blog publishing with Facebook packaging.

## Main Responsibilities

1. define WordPress publishing requirements,
2. define Facebook packaging templates,
3. define the queue and approval workflow,
4. define mapping from blog posts to Facebook posts,
5. define scheduled publishing behavior.

## Current Planning Baseline

The current planning baseline for Phase 3 is now documented in:

1. [WORDPRESS_PUBLISHING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_PUBLISHING_CONTRACT_V1.md)
2. [WORDPRESS_REST_TRANSPORT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_REST_TRANSPORT_V1.md)
3. [FACEBOOK_PACKAGING_TEMPLATE_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_PACKAGING_TEMPLATE_CONTRACTS_V1.md)
4. [DISTRIBUTION_QUEUE_MODEL_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_QUEUE_MODEL_V1.md)
5. [BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md)
6. [PUBLISH_HISTORY_SCHEMA.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_SCHEMA.md)
7. [APPROVAL_WORKFLOW.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/APPROVAL_WORKFLOW.md)
8. [DISTRIBUTION_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_HEALTH_REPORTING_V1.md)
9. [WORDPRESS_TRANSPORT_VALIDATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_TRANSPORT_VALIDATION_V1.md)
10. [FACEBOOK_TRANSPORT_VALIDATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_TRANSPORT_VALIDATION_V1.md)
11. [DISTRIBUTION_SCHEDULE_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_SCHEDULE_REPORTING_V1.md)
12. [PHASE_3_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_EXECUTION_PLAN.md)
13. [PHASE_3_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_VALIDATION_PLAN.md)

## Current Implementation Status

Phase 3 is now implementation-complete for the accepted v1 scope, and the formal closeout baseline is recorded in:

1. [PHASE_3_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT.md)
2. [PHASE_3_CLOSEOUT_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT_CHECKLIST.md)
3. [PHASE_3_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_RESIDUAL_ITEMS.md)

The current repo baseline already answers:

1. what a WordPress-ready payload must contain,
2. what Facebook package families exist first,
3. what queue states mean,
4. how blog and Facebook outputs should be linked,
5. what must be validated before public publishing logic is trusted.

The current repo already implements:

1. deterministic WordPress payload rendering from an approved draft,
2. append-only local blog publish record storage,
3. operator-facing local WordPress preparation through a CLI,
4. deterministic Facebook package derivation from an approved draft,
5. append-only local social package record storage,
6. operator-facing local Facebook package preparation through a CLI with duplicate-primary protection,
7. initial queue-record creation for blog and Facebook workflow state,
8. initial blog-to-Facebook mapping record creation with selected output preservation,
9. manual social-package review logging with refreshed queue and mapping snapshots,
10. local WordPress publish-state updates with refreshed queue and mapping snapshots,
11. dedicated local Facebook publish-state records with explicit `facebook_publish_id` tracking,
12. local Facebook publish-state updates that move queue and mapping records into scheduled, published, and failed end states,
13. conservative scheduling policy rules that preserve manual versus auto scheduling metadata and prevent Facebook scheduling ahead of the linked blog schedule.
14. the first real WordPress transport slice using WordPress REST with application-password auth, dry-run request preview, remote draft create/update support, and append-only local failure recording.
15. the first real Facebook transport slice using the Facebook Graph Page feed endpoint with dry-run request preview, publish and schedule support, and append-only local success and failure recording.
16. operator-facing distribution health reporting with queue, mapping, transport, schedule-collision, and broken-chain consistency visibility.
17. operator-facing WordPress and Facebook transport validation entry points for non-mutating environment checks.
18. shared retry/backoff support for transient WordPress and Facebook transport failures.
19. operator-facing schedule planning reporting for schedule-ready and collision-heavy chains.

The current repo does not yet implement:

1. proof that the operator's real external WordPress and Facebook credentials have already been validated live,
2. a visual schedule dashboard beyond the current CLI planning report,
3. comment-CTA auto-posting as a second Facebook transport step.

The current implementation evidence for this phase is recorded in:

1. [PHASE_3_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_1.md)
2. [PHASE_3_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_2.md)
3. [PHASE_3_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_3.md)
4. [PHASE_3_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_4.md)
5. [PHASE_3_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_5.md)
6. [PHASE_3_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_6.md)
7. [PHASE_3_ACCEPTANCE_BATCH_7.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_7.md)
8. [PHASE_3_ACCEPTANCE_BATCH_8.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_8.md)
9. [PHASE_3_ACCEPTANCE_BATCH_9.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_9.md)

## Required Outputs

1. WordPress publishing contract,
2. Facebook hook template families,
3. Facebook caption template families,
4. comment CTA template families,
5. queue-state model,
6. publish mapping records.

## Key Decisions Now Locked

1. the first Facebook posting path is the Facebook Graph Page feed transport,
2. scheduling remains conservative, explicit, and metadata-rich rather than hidden automation,
3. the first social-package baseline is intentionally narrow and deterministic instead of variant-heavy,
4. human review remains part of the publish path for both blog and Facebook outputs.

The first WordPress transport decision is now locked in:

1. [WORDPRESS_REST_TRANSPORT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_REST_TRANSPORT_V1.md)

## Things This Phase Must Not Do

1. expand to Facebook Groups,
2. expand to paid boosts,
3. add complex analytics,
4. add multi-channel social publishing,
5. bypass human review in the name of speed.

## Risks

1. treating social packaging as a weak afterthought,
2. over-automating low-quality content into public channels,
3. unclear queue states,
4. fragile publishing logic,
5. inconsistent mapping between blog and Facebook outputs.

## Definition Of Done

Phase 3 is done when:

1. an approved draft can be published to WordPress,
2. Facebook-ready assets can be generated from that draft,
3. the operator can review and queue both outputs,
4. the source-to-blog-to-Facebook chain is traceable,
5. the operator can see collision and broken-state warnings before trusting the chain.

## Handoff To Phase 4

Phase 4 should use the publish flow from this phase as the basis for structured tracking. If mappings are weak here, later analytics will be weak as well.

## Entry Control

Reference:

1. [PHASE_2_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT.md)
2. [PHASE_3_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_ENTRY_CHECKLIST.md)
3. [PHASE_3_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_EXECUTION_PLAN.md)
4. [PHASE_3_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_VALIDATION_PLAN.md)

## Closeout Control

Reference:

1. [PHASE_3_CLOSEOUT_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT_CHECKLIST.md)
2. [PHASE_3_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT.md)
3. [PHASE_3_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_RESIDUAL_ITEMS.md)
4. [PHASE_4_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_ENTRY_CHECKLIST.md)
