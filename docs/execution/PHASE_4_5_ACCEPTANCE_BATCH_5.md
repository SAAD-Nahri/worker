# Phase 4.5 Acceptance Batch 5

## Purpose

This batch records the replacement of the original technical canary with a cleaner manually refined activation canary.

The goal of this batch was to prove:

1. the repo can carry a manually refined approved draft through the normal append-only workflow,
2. the replacement canary can create a fresh live WordPress draft,
3. the activation blocker is now the final public blog step, not draft quality inside the repo.

## Scope

Included in this batch:

1. manual refinement of the current best canary draft into a cleaner approved snapshot,
2. preparation of a new blog publish record from that refined draft,
3. creation and approval of an explicit replacement social package,
4. refreshed linkage for the replacement chain,
5. live WordPress draft creation for the replacement canary.

Not included in this batch:

1. public WordPress publish,
2. public WordPress schedule,
3. Facebook publish,
4. Facebook schedule,
5. formal Phase 4.5 closeout.

## What Changed

The earlier technical canary remained useful for transport proof, but its copy quality was not strong enough for a public activation run.

A new manual refinement snapshot was appended for:

1. `draft_id=draft-0637ac87046e-20260402T223513Z-f74c7982`

The refined version replaced weak placeholder phrasing with direct storage and safety framing:

1. short-term reuse is allowed,
2. only cool and low-acid foods are recommended,
3. heat, grease, and acidic foods are discouraged,
4. the plastic should be retired once it looks worn.

The refined draft was then re-approved through the normal review workflow.

## Commands Run

### Re-approve the refined draft

```powershell
python src\cli\review_draft.py --draft-id draft-0637ac87046e-20260402T223513Z-f74c7982 --outcome approved --note "phase_4_5_live_canary: manually refined copy accepted for the public activation canary."
```

### Prepare the replacement publish record

```powershell
python src\cli\prepare_wordpress_publish.py --draft-id draft-0637ac87046e-20260402T223513Z-f74c7982 --publish-intent draft
```

Observed result:

1. `blog_publish_id=blog-draft-0637ac-20260404T202650.440295+0000-e4f08c4c`

### Prepare and approve the replacement social package

```powershell
python src\cli\prepare_facebook_package.py --draft-id draft-0637ac87046e-20260402T223513Z-f74c7982 --blog-publish-id blog-draft-0637ac-20260404T202650.440295+0000-e4f08c4c --allow-repackage
python src\cli\review_social_package.py --social-package-id social-draft-0637ac-20260404T202714.535914+0000-6516d378 --outcome approved --note "phase_4_5_live_canary: approved package for the replacement activation canary."
python src\cli\prepare_distribution_linkage.py --blog-publish-id blog-draft-0637ac-20260404T202650.440295+0000-e4f08c4c --social-package-id social-draft-0637ac-20260404T202714.535914+0000-6516d378 --allow-refresh
```

Observed result:

1. `social_package_id=social-draft-0637ac-20260404T202714.535914+0000-6516d378`
2. replacement chain linkage was refreshed successfully.

### Create the live replacement WordPress draft

```powershell
python src\cli\sync_wordpress_transport.py --blog-publish-id blog-draft-0637ac-20260404T202650.440295+0000-e4f08c4c --config-path config\wordpress_rest_config.local.json --execute
```

Observed result:

1. remote WordPress operation: `create_draft`,
2. remote post id: `25`,
3. remote post URL: `https://kuchniatwist.pl/?p=25`,
4. local WordPress status: `draft_created`.

## Current Replacement Canary State

Replacement canary identifiers:

1. `draft_id=draft-0637ac87046e-20260402T223513Z-f74c7982`
2. `blog_publish_id=blog-draft-0637ac-20260404T202650.440295+0000-e4f08c4c`
3. `social_package_id=social-draft-0637ac-20260404T202714.535914+0000-6516d378`
4. `wordpress_post_id=25`
5. `wordpress_post_url=https://kuchniatwist.pl/?p=25`

Operator-facing chain state:

1. blog queue state: `wordpress_draft_created`
2. Facebook queue state: `approved_for_queue`
3. mapping status: `packaged_social_pending`
4. activation signal: `awaiting_live_canary_execution`

## Important Clarification

The replacement canary is cleaner than the original technical draft, but the system still cannot honestly claim a finished live canary until the blog post reaches a public or scheduled state.

Facebook transport is correctly blocked until that happens.

## Recommendation

The next activation steps should be:

1. open WordPress draft `25` in the site admin,
2. do a quick final visual/content check,
3. publish or schedule the draft in WordPress,
4. record that blog state locally,
5. execute the Facebook canary,
6. review distribution health, publish-chain history, and tracking audit,
7. then write the formal Phase 4.5 closeout.
