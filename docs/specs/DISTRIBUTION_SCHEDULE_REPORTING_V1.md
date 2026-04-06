# Distribution Schedule Reporting V1

## Purpose

This document defines the first operator-facing schedule planning report for Phase 3.

The report exists to answer:

1. which chains are ready for blog scheduling,
2. which chains are ready for Facebook scheduling,
3. which chains are already scheduled as a pair,
4. which scheduled rows collide,
5. which scheduled blog items still need the Facebook side completed.

## Core Rule

The schedule report is a planning view, not a source of truth.

It is derived from the latest append-only distribution records and must not invent a second scheduling state machine.

## Input Sources

The report should derive from:

1. latest blog publish records,
2. latest social package records,
3. latest Facebook publish records,
4. latest queue item records,
5. latest mapping records.

## Required Summary Fields

The summary must preserve at minimum:

1. total rows,
2. scheduling-signal counts,
3. blog schedule slot counts,
4. Facebook schedule slot counts,
5. row count with schedule alerts,
6. schedule-alert counts,
7. ready-for-blog-schedule count,
8. ready-for-Facebook-schedule count,
9. scheduled-pair count,
10. awaiting-Facebook-schedule count.

## Required Row Fields

Each row should preserve at minimum:

1. `blog_publish_id`
2. `wordpress_title`
3. `blog_queue_state`
4. `facebook_queue_state`
5. `scheduled_for_blog`
6. `scheduled_for_facebook`
7. `scheduling_signal`
8. `schedule_alerts`
9. `operator_signal`

## Scheduling Signals

The v1 report should surface bounded, readable planning signals such as:

1. `ready_for_blog_schedule`
2. `ready_for_facebook_schedule`
3. `ready_for_facebook_publish`
4. `scheduled_pair`
5. `awaiting_facebook_schedule`
6. `facebook_scheduled`
7. `published_pair`
8. `collision_review`
9. `monitor`

These signals should summarize planning state rather than replace the underlying queue records.

## Alert Rule

If the health layer already marks a row with schedule alerts, the schedule report should surface:

1. the row,
2. the current slot values,
3. the alert labels,
4. a planning signal that prioritizes operator review.

## CLI Contract

Text summary:

`python src\cli\summarize_distribution_schedule.py`

JSON output:

`python src\cli\summarize_distribution_schedule.py --json`

## Definition Of Done

This spec is satisfied when:

1. the operator has a dedicated schedule planning report,
2. the report can distinguish ready, scheduled, and collision states,
3. the report is derived from existing append-only runtime records instead of inventing a new workflow layer.
