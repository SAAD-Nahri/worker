# Phase 4.9 Acceptance Batch 8

## Purpose

Close more of the real approval-UI deployment gap before live WordPress-admin testing.

## Work Completed

1. Added plugin-side Operator API reachability guidance on the Settings page.
2. Added the same reachability guidance to the Validation page so localhost and internal-network assumptions are visible before manual click-through testing starts.
3. Added concrete reverse-proxy deployment examples for:
   1. `nginx`
   2. `Caddy`
4. Updated the runtime and approval runbooks so hosted WordPress deployments now have a specific, documented path instead of only a warning.

## Why This Matters

The previous baseline could start the operator API locally, but it still left one serious practical gap:

1. a hosted WordPress site cannot use `127.0.0.1` on the worker machine.

This batch does not pretend to solve network topology automatically, but it removes ambiguity and makes the correct deployment path explicit in both the plugin shell and the repo docs.

## Validation

1. `python -m unittest discover -s tests -v`
2. Plugin PHP still requires live WordPress-admin validation because PHP CLI is not available in the local repo environment.

## Remaining Phase 4.9 Gap

1. install or refresh the plugin in real WordPress admin,
2. verify the new Settings and Validation guidance render correctly,
3. complete the live draft/social/queue review click-through.
