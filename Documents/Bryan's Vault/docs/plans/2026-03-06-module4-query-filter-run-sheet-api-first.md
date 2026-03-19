# Module 4 Hardening Run Sheet - API Command First (No UI)

Date: 2026-03-06
Scenario Name: CV Intake Pipeline v2
Scenario ID: 4162531
Team Path: 200002
Use Case: Make UI blocked by "orphans" error
Scope: Module 4 query-filter hardening only

## Non-Negotiables

- No UI edits at any step.
- Keep scenario inactive during blueprint edits.
- Change only Module 4 logic.
- Preserve modules 6/7 router filter behavior.

## Required Known IDs

- Scenario ID: `4162531`
- Patch target module: `4` (`Notion searchObjects1`)
- Protected modules:
  - `6` create path
  - `7` update path
- Existing route gates (must remain unchanged):
  - Module 6 filter: `{{4.id}}` does not exist
  - Module 7 filter: `{{4.id}}` exists

## API Execution Flow

### 0) Preflight Snapshot

```text
ACTION: Get scenario details + current blueprint
OUTPUT: scenario metadata + blueprint JSON
SAVE: prepatch-blueprint-4162531-YYYYMMDD-HHMM.json
VERIFY: module IDs 4/6/7 present
```

### 1) Deactivate Scenario

```text
ACTION: scenarios_deactivate (4162531)
VERIFY: scenario state = inactive
ABORT IF: deactivate call fails
```

### 2) Patch Blueprint (Module 4 Only)

Patch objective:

- Add candidate-name query filtering to module 4 Notion search.
- Map canonical parser name (trimmed/normalized) to search query.
- Keep result cap conservative (`<= 5`).
- Keep module 4 output compatible with `{{4.id}}` exist/nExist gates.

Patch safety checks before submit:

```text
[ ] Module 4 modified
[ ] Modules 6/7 filters unchanged
[ ] Module 7 mapper unchanged from known-good
[ ] No type mapping regressions introduced
```

Submit:

```text
ACTION: scenarios_update / flow update with patched blueprint
VERIFY: isinvalid = false
SAVE: postpatch-blueprint-4162531-YYYYMMDD-HHMM.json
IF FAIL: restore prepatch blueprint and reactivate
```

### 3) Reactivate Scenario

```text
ACTION: scenarios_activate (4162531)
VERIFY: scenario state = active
ABORT IF: activate call fails
```

### 4) Run API-Driven Validation Set

Run controlled payload tests by triggering webhook/API inputs; do not use UI runner.

#### Test A - New Candidate

```text
INPUT: synthetic name not in Notion Candidates
EXPECT: module 4 no match -> create path only
PASS: exactly one route, one create, no update
```

#### Test B - Exact Duplicate

```text
INPUT: exact existing candidate name
EXPECT: module 4 match -> update path only
PASS: exactly one route, no new create
```

#### Test C - Near-Match Variant

```text
INPUT: punctuation/case variant
EXPECT: deterministic behavior (documented)
PASS: no double-fire, no wrong-record update
```

#### Test D - Ambiguous Common Name

```text
INPUT: common name returning multiple potential records
EXPECT: fail-safe behavior (no arbitrary update)
PASS: no wrong-record update, no double-fire
```

### 5) Pull Execution Logs by API

```text
ACTION: list recent executions for scenario 4162531
CAPTURE: run ID, status, ops count, route/module path, error text
VERIFY: each test outcome aligns with expected route behavior
```

## Rollback Protocol (API Only)

Trigger rollback if any of these occur:

- `isinvalid != false`
- any test double-fires routes
- wrong-record update in ambiguous test
- Notion validation/type errors reappear

Rollback steps:

```text
1) Deactivate scenario 4162531
2) Re-apply prepatch blueprint snapshot
3) Validate (isinvalid = false)
4) Reactivate scenario
5) Confirm last-known-good execution success
```

## Evidence Log Template

```text
Scenario: 4162531
Patch Run Timestamp: __________________

Prepatch Blueprint File: __________________
Postpatch Blueprint File: __________________

Test A Run ID: ______  Status: ______  Route: ______  Error: ______
Test B Run ID: ______  Status: ______  Route: ______  Error: ______
Test C Run ID: ______  Status: ______  Route: ______  Error: ______
Test D Run ID: ______  Status: ______  Route: ______  Error: ______

Created Page IDs: ______________________
Updated Page IDs: ______________________

GO/NO-GO: _____________________________
Operator: _____________________________
```

## Completion Criteria

Mark complete only when all are true:

```text
[ ] 4/4 test cases pass
[ ] No double-route executions
[ ] No Notion API validation/type failures
[ ] Duplicate detection improved for exact-name case
[ ] Ambiguous-name case does not update arbitrary record
```

## Post-Completion Updates

After GO:

```text
[ ] Update config/make-scenarios.json (remove Module 4 known issue if resolved)
[ ] Update review/weekly-sync-audit-template.md hardening note
[ ] Add Notion tracker session with API test run IDs
[ ] Mark TODO task complete
```

## Related Docs

- Operator shell (UI-assisted): `docs/plans/2026-03-06-module4-query-filter-run-sheet-operator-shell.md`
- Generic run sheet: `docs/plans/2026-03-06-module4-query-filter-run-sheet.md`
- Hardening checklist: `docs/plans/2026-03-06-module4-query-filter-hardening-checklist.md`
