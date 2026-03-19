# Module 4 Hardening Run Sheet - Operator Shell (Pre-Filled)

Date: 2026-03-06
Scenario Name: CV Intake Pipeline v2
Scenario ID: 4162531
Team ID Path: 200002
Window Type: Live patch (single operator pass)
Change Scope: Module 4 query filtering only

## Fixed IDs and Targets

- Scenario: `4162531`
- Module 4 (target patch module): `4` (`Notion searchObjects1`)
- Module 6 (create route, do not edit): `6`
- Module 7 (update route, do not edit): `7`
- Router gate logic (already live, do not change):
  - Module 6 route filter: `{{4.id}}` does not exist
  - Module 7 route filter: `{{4.id}}` exists

## Operator Rules

- Keep scenario inactive during edits.
- Touch Module 4 only.
- Do not modify modules 6/7 filters.
- Stop immediately on unexpected schema or mapper validation errors.

## Preflight (Copy/Paste)

```text
[x] Confirm scenario ID: 4162531
[x] Confirm target module ID: 4
[x] Confirm protected modules: 6 (create), 7 (update)
[ ] Capture current state screenshot + run history
[ ] Export/save pre-patch blueprint snapshot
[ ] Confirm rollback file path recorded
```

## Artifact Names (Pre-Filled)

```text
Pre-patch blueprint: prepatch-blueprint-4162531-YYYYMMDD-HHMM.json
Post-patch blueprint: postpatch-blueprint-4162531-YYYYMMDD-HHMM.json
Execution evidence log: module4-hardening-evidence-4162531-YYYYMMDD.md
```

## Field Mapping Lock (Fill These 4 Fields Before Patch)

```text
Parser payload candidate full-name key: ______________________
Parser fallback key(s) (if full name missing): _______________
Notion Candidates title property name: _______________________
Notion data_source ID used by Module 4: ______________________
```

Normalization requirement:

```text
trim -> collapse spaces -> canonical full name
```

## One-Shot Execution Script

### 1) Deactivate Scenario

```text
ACTION: Deactivate scenario 4162531
VERIFY: Status shows Inactive
```

### 2) Backup Blueprint

```text
ACTION: Export current blueprint
SAVE: prepatch-blueprint-4162531-YYYYMMDD-HHMM.json
VERIFY: File readable and timestamped
```

### 3) Patch Module 4 Only

Patch intent (copy/paste notes):

```text
PATCH TARGET: Module 4 (Notion searchObjects1)
PATCH GOAL: Add candidate-name query/filter mapping from canonical parser name
RESULT LIMIT: <= 5
DO NOT CHANGE: Module 6 filter, Module 7 filter, create/update module mappings
COMPATIBILITY: Keep output shape compatible with {{4.id}} exist/nExist gating
```

### 4) Validate Blueprint

```text
ACTION: Submit updated blueprint
VERIFY: isinvalid = false
IF FAIL: STOP -> restore prepatch blueprint -> reactivate last-known-good
```

### 5) Reactivate Scenario

```text
ACTION: Reactivate scenario 4162531
VERIFY: Status shows Active
```

## Controlled Test Script (A/B/C/D)

### Test A - New Candidate

```text
INPUT: synthetic name not present in Candidates DB
EXPECT: Module 4 no match -> Module 6 route only
PASS: one route, one create, no update call
Run ID: __________________
```

### Test B - Exact Duplicate

```text
INPUT: known existing candidate name
EXPECT: Module 4 match -> Module 7 route only
PASS: one route, update only, no new page
Run ID: __________________
```

### Test C - Near-Match Variant

```text
INPUT: punctuation/case variant of existing candidate name
EXPECT: deterministic behavior (document rule)
PASS: no double-fire, no wrong-record update
Run ID: __________________
```

### Test D - Ambiguous Common Name

```text
INPUT: common name likely matching multiple records
EXPECT: fail-safe behavior (no arbitrary update)
PASS: no wrong-record update, no double-fire
Run ID: __________________
```

## Evidence Capture Table (Fill Live)

```text
A | Route: ______ | Result: ______ | Page ID: ______ | Error: ______
B | Route: ______ | Result: ______ | Page ID: ______ | Error: ______
C | Route: ______ | Result: ______ | Page ID: ______ | Error: ______
D | Route: ______ | Result: ______ | Page ID: ______ | Error: ______
```

## GO / NO-GO Gate

Mark GO only if all checked:

```text
[ ] 4/4 tests passed
[ ] No double-route execution in any test
[ ] No Notion validation/type errors
[ ] No duplicate create for known existing candidate
[ ] No wrong-record update in ambiguous-name test
```

If any unchecked -> NO-GO:

```text
ACTION: Restore prepatch blueprint
ACTION: Reactivate last-known-good config
ACTION: Log failing payload, run ID, module error
```

## Post-Run Updates (Copy/Paste)

```text
[ ] Update config/make-scenarios.json: remove Module 4 known issue if GO
[ ] Update review/weekly-sync-audit-template.md: note hardening completion
[ ] Add new Notion tracker session with run IDs + outcomes
[ ] Mark TODO item complete if GO
```

## Quick Links

- Base checklist: `docs/plans/2026-03-06-module4-query-filter-hardening-checklist.md`
- Generic run sheet: `docs/plans/2026-03-06-module4-query-filter-run-sheet.md`
- This operator shell: `docs/plans/2026-03-06-module4-query-filter-run-sheet-operator-shell.md`
- API-first variant (no UI): `docs/plans/2026-03-06-module4-query-filter-run-sheet-api-first.md`
