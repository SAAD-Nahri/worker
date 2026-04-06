# Phase 4.9 Acceptance Batch 6

## Scope

This acceptance batch records the queue-actionability and dashboard-navigation hardening pass for the Approval UI baseline.

The goal of this batch is to prove that:

1. failed queue items no longer present `Approve` as if it were valid when the backend would reject it,
2. queue inbox and queue detail now expose explicit approve block reasons before submit,
3. dashboard recent activity now carries safe detail-target hints for draft, social-package, and queue review items,
4. current alerts now carry queue-detail targets when the alert can be traced to a concrete queue item,
5. the WordPress admin shell can use those hints to navigate the operator directly into the relevant review detail page.

## What Changed

### Operator API

The operator API now returns richer actionability and navigation context.

Queue inbox rows now include:

1. `approve_allowed`
2. `approve_block_reason`
3. `schedule_allowed`
4. `schedule_block_reason`

Queue detail payloads now expose the same action availability context, so failed queue items can be shown honestly before the operator tries to review them.

Dashboard activity rows now include:

1. `detail_target_type`
2. `detail_target_id`

Current alert rows now include:

1. `queue_item_id` when a concrete queue-detail target can be resolved safely from the live runtime state.

### WordPress admin plugin shell

The plugin now uses the dashboard context as navigation instead of dead display-only rows.

Recent Review Activity now links into:

1. draft detail,
2. social-package detail,
3. queue-item detail.

Current Alerts now link into queue detail when the alert can be traced to a concrete queue item.

Queue inbox and queue detail now hide the direct `Approve` action when the backend marks the item as not approvable and show the operator the block reason instead.

## Validation Baseline

Focused validation:

```powershell
python -m unittest tests.unit.operator_api.test_app -v
```

Full repository baseline:

```powershell
python -m unittest discover -s tests -v
```

Accepted result:

1. focused operator API suite green,
2. full repository suite green at `226` tests passing.

## Known Limit

The plugin still requires live WordPress-admin validation because PHP CLI is not available in the local repo environment.

So this batch is accepted as:

1. safer queue-actionability guidance,
2. faster dashboard-to-detail navigation,
3. repo baseline preserved,
4. still awaiting real admin verification.
