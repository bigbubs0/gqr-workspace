# Module 4 Hardening Run Sheet (One-Shot)

Date: 2026-03-06
Scenario: CV Intake Pipeline v2 (`4162531`)
Window Type: Live patch (single operator pass)
Change Scope: Module 4 query filtering only

## Operator Rules

- Keep scenario inactive during edits.
- Touch Module 4 only.
- Do not modify router filters on modules 6/7.
- Stop immediately on any unexpected schema/mapper error.

## Preflight (2 minutes)

Copy/paste checklist:

```text
[ ] Confirm scenario ID: 4162531
[ ] Confirm current state captured (screenshot + run history)
[ ] Export and save pre-patch blueprint snapshot
[ ] Confirm rollback path is available
```

Artifacts to save:

- `prepatch-blueprint-4162531-YYYYMMDD-HHMM.json`
- `postpatch-blueprint-4162531-YYYYMMDD-HHMM.json`

## Field Mapping Lock (No-Guess Zone)

Before patching Module 4, confirm these exact values:

```text
Candidate name from parser payload key: ____________________
Fallback key(s) if full name missing: ______________________
Notion Candidates title property name: _____________________
Notion data_source ID used by Module 4: ____________________
```

Normalization rule to apply in query mapping:

```text
trim -> collapse spaces -> canonical full name
```

## Execution Script

### Step 1: Deactivate

```text
ACTION: Deactivate scenario 4162531
VERIFY: Scenario status = Inactive
```

### Step 2: Backup Blueprint

```text
ACTION: Export current blueprint
SAVE AS: prepatch-blueprint-4162531-YYYYMMDD-HHMM.json
VERIFY: File present and readable
```

### Step 3: Patch Module 4 Only

Implementation target:

- Add explicit candidate-name query/filter mapping in Module 4 Notion search.
- Keep result limit conservative (prefer 1-5).
- Preserve output compatibility with existing router conditions (`{{4.id}}` exist/nExist).

Copy/paste patch intent block (for your API editor notes):

```text
PATCH TARGET: module 4 (Notion searchObjects1)
CHANGE: Add candidate-name query filter mapped from canonical parser name
DO NOT CHANGE: modules 6/7 filters, downstream create/update mappings
LIMIT: <= 5
```

### Step 4: Validate Blueprint

```text
ACTION: Submit updated blueprint
VERIFY: isinvalid = false
IF FAIL: stop, restore prepatch blueprint, reactivate last-known-good
```

### Step 5: Reactivate

```text
ACTION: Reactivate scenario 4162531
VERIFY: Scenario status = Active
```

## Controlled Test Script (Run in Order)

### Test A - New Candidate

```text
INPUT: synthetic name not in Notion
EXPECT: Module 4 no match -> Create route only
PASS IF: one route only, one new page, no update call
```

### Test B - Exact Duplicate

```text
INPUT: known existing candidate name
EXPECT: Module 4 match -> Update route only
PASS IF: one route only, no new page created
```

### Test C - Near-Match Variant

```text
INPUT: punctuation/case variation of existing name
EXPECT: deterministic behavior (document whether create or update)
PASS IF: no double-fire, no wrong-record update
```

### Test D - Ambiguous Common Name

```text
INPUT: common name likely to return multiple records
EXPECT: fail-safe behavior (no arbitrary update)
PASS IF: no wrong-record update, no double-fire
```

## Evidence Capture (Required)

Fill this during execution:

```text
Run ID A: __________________  Route: ______  Result: ______
Run ID B: __________________  Route: ______  Result: ______
Run ID C: __________________  Route: ______  Result: ______
Run ID D: __________________  Route: ______  Result: ______

Created page IDs: _________________________________________
Updated page IDs: _________________________________________
Errors (if any): __________________________________________
```

## Go/No-Go Gate

Mark `GO` only if all are true:

```text
[ ] 4/4 tests passed
[ ] No double-route execution
[ ] No Notion validation/type errors
[ ] No duplicate create for known existing candidate
[ ] No wrong-record update on ambiguous test
```

If any box fails, mark `NO-GO`:

```text
ACTION: Restore prepatch blueprint
ACTION: Reactivate last-known-good config
ACTION: Log failure payload + run ID + module error
```

## Post-Run Updates (5 minutes)

After GO:

```text
[ ] Update config/make-scenarios.json (remove Module 4 known gap)
[ ] Update weekly-sync-audit-template.md with hardening complete note
[ ] Add new session log entry to Notion tracker with run IDs and outcomes
```
