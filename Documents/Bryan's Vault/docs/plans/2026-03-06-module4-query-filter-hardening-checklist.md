# Module 4 Query-Filter Hardening Checklist (Pre-Production)

Date: 2026-03-06
Scenario: CV Intake Pipeline v2 (`4162531`)
Target Module: 4 (`Notion searchObjects1` duplicate lookup)
Goal: Replace broad/ambiguous duplicate lookup with deterministic candidate-name matching to reduce false update routing.

Operator run sheet: `docs/plans/2026-03-06-module4-query-filter-run-sheet.md`

## Guardrails

- Keep scenario `4162531` inactive during blueprint edits.
- Change only Module 4 query/filter logic in this pass.
- Do not modify router filters in modules 6/7 (already verified).
- Capture blueprint export before and after patch.

## Current Risk

- Module 4 may return up to 5 arbitrary records when no name filter is applied.
- Router gate currently depends on `{{4.id}}` exist/nExist, so broad results can incorrectly route to update path.

## Field Mapping Checklist

Use this order to avoid guessing:

1. Confirm webhook payload source fields

- Candidate full name field from CV parser output (example: `full_name`).
- Optional fallback fields if parser splits names (`first_name`, `last_name`).

1. Confirm Notion Candidates data source target property

- Property used for candidate display name (title property, often `Name`).
- Confirm exact property type in data source schema.

1. Normalize values before search

- Trim whitespace.
- Collapse repeated spaces.
- Lowercase for comparison if Make expression path supports it.
- Build canonical key:
  - Preferred: full name normalized (`first + last` if full missing).

1. Module 4 query design

- Apply explicit query filter to Candidates data source using canonical candidate name.
- Limit results to minimal set for dedupe decision (1-5 max).
- If API supports exact-match style filter, prefer exact over contains.

1. Router compatibility check

- Ensure post-search output remains compatible with existing router filters:
  - Create route: `{{4.id}}` does not exist
  - Update route: `{{4.id}}` exists
- If search output shape changes, adjust route conditions accordingly before reactivation.

## Surgical Patch Steps

1. Deactivate scenario `4162531`.
2. Export current blueprint snapshot and save as rollback artifact.
3. Edit Module 4 only:

- Add candidate-name query/filter to Notion search operation.
- Map canonical candidate-name value from parser output.
- Keep result limit conservative.

1. Validate blueprint (`isinvalid: false`).
2. Reactivate scenario.

## Test Matrix (Must Pass Before Production Confidence)

Use controlled payloads in this exact order.

### Test A: New Candidate (No Existing Record)

- Input: synthetic CV name not present in Candidates DB.
- Expected:
  - Module 4 returns no match.
  - Router takes create route only.
  - New candidate page created once.
  - No update module call.

### Test B: Exact Duplicate (Existing Record)

- Input: CV name exactly matching existing candidate.
- Expected:
  - Module 4 returns existing candidate.
  - Router takes update route only.
  - Existing candidate updated.
  - No new page created.

### Test C: Near-Match Name Variant

- Input: minor punctuation/case variation (for example, "Anne-Marie Smith" vs "Anne Marie Smith").
- Expected:
  - Deterministic behavior documented.
  - No double-fire.
  - If no exact match strategy is used, confirm whether create or update path is desired and consistent.

### Test D: Ambiguous Common Name

- Input: common name likely to return multiple records.
- Expected:
  - No arbitrary update of wrong record.
  - If multiple matches returned, route should fail-safe (recommended: no auto-update, flag for manual review).

## Pass/Fail Criteria

Pass only if all are true:

- 4/4 tests produce expected route behavior.
- No run produces both create and update route execution.
- No Notion validation/type errors.
- No duplicate creation for known existing profile.
- No wrong-record updates in ambiguous-name test.

## Rollback Plan

- If any test fails, deactivate scenario and restore pre-patch Module 4 blueprint snapshot.
- Reactivate last known-good version.
- Document failing test case and payload.

## Evidence to Capture

- Scenario execution IDs for all tests.
- Module 4 output snippet for each test.
- Route taken (create/update) per test.
- Notion record IDs created/updated.

## Post-Patch Update Targets

After successful hardening, update:

- `Documents/Bryan's Vault/config/make-scenarios.json` (remove Module 4 known issue)
- `Documents/Bryan's Vault/review/weekly-sync-audit-template.md` (note duplicate-check hardening complete)
- Notion page `Google Drive Organization - Progress Tracker` with test evidence summary.
