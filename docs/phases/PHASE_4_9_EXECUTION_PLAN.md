# Phase 4.9 Execution Plan

## Purpose

This plan turns Approval UI work into a sequence of practical slices instead of a vague "we need a dashboard later" promise.

The goal is to build a review-first operator console without creating a second workflow engine.

## Recommended Build Order

### Slice 1: Backend operator API

Objective:

1. expose review-safe operator workflows through one private API,
2. keep the repo runtime authoritative.

Deliverables:

1. operator API package,
2. shared-secret auth,
3. dashboard endpoint,
4. dashboard activity and alert visibility,
5. inbox/detail/review endpoints,
6. combined health endpoint.

Out of scope:

1. public-facing API,
2. analytics API,
3. media management API.

### Slice 2: Queue review and scheduling gate

Objective:

1. make queue approval a first-class append-only workflow,
2. allow narrow schedule actions from the UI without bypassing current contracts,
3. support explicit removal from the current batch without inventing a second queue system,
4. expose approve and schedule actionability clearly so the UI does not offer actions the backend would reject.

Deliverables:

1. queue review record,
2. queue review storage helpers,
3. queue review API path,
4. blog queue scheduling path from the UI,
5. explicit queue-removal outcome in the operator path,
6. explicit approve and schedule block reasons in queue-facing payloads.

Out of scope:

1. Facebook scheduling shortcut from the UI,
2. automatic queue approvals,
3. publish actions hidden inside review actions.

### Slice 3: WordPress admin plugin shell

Objective:

1. give the operator one familiar admin surface for review,
2. keep WordPress in the role of shell, not workflow owner.

Deliverables:

1. plugin menu and settings,
2. dashboard page,
3. draft review inbox/detail,
4. social review inbox/detail,
5. queue review inbox/detail,
6. validation page,
7. settings and shared-secret config.

Out of scope:

1. full post editing,
2. custom workflow tables,
3. analytics dashboards,
4. media manager.

### Slice 4: Validation and hardening

Objective:

1. prove the backend paths are stable,
2. make the operator shell faster to use in real review sessions,
3. record what still requires live plugin validation.

Deliverables:

1. Python backend tests,
2. phase acceptance evidence,
3. approval UI runbook,
4. dashboard activity and alert navigation into detail screens when a safe target exists,
5. dedicated live-validation support inside the plugin and operator API,
6. explicit note of the PHP validation gap.

Out of scope:

1. autoapproval,
2. score-assisted fast lane,
3. deep UI redesign.

## Default Rule

The Approval UI should remain review-only in V1.

It should help the operator:

1. review,
2. approve,
3. hold,
4. schedule safely,
5. inspect current workflow state.

It should not become a place where the workflow logic is reinvented.
