# Drive + Notion Workflow Recovery (2026-03-06)

## What likely stopped in mid-Feb

1. Workflow execution appears to end at 2026-02-18, then workspace migration happened 2026-02-24 to 2026-02-26.
2. `config/` in the active vault is empty, and `TODO.md` still shows `Populate /config/make-scenarios.json` unchecked.
3. Without a populated local manifest, no reliable source of current scenario IDs, webhook URLs, or run-state tracking remained in the active workspace.

## Recovery status

- Manifest created: `config/make-scenarios.json`
- Runbook created: this file
- Agent created: `.github/agents/notion-drive-workflow-operator.agent.md`
- Make.com API activation: complete (`4162531` ON)
- OpenAI parsing bug: fixed (`rawText` coerced with `toString()`)
- Connection checks on activation: passed (Google Drive `7427128`, OpenAI `622584`, Notion `622561`)
- External systems restart: partially complete (Apps Script UI checks still pending)

## Resume checklist (run in this order)

1. Make.com scenario health

- Open scenario `4162531` (CV Intake Pipeline v2).
- Confirm scenario is still ON (already activated via API this session).
- Add router filter conditions in UI:
  - Route 1 (create): run only when duplicate count is `0`
  - Route 2 (update): run only when duplicate count is `> 0`
- Trigger one manual run and confirm exactly one route fires.

1. Apps Script triggers

- Open each Apps Script project:
  - CV Auto-Sort
  - Index Updater
  - Weekly Auto-Archive
- In `Triggers`, confirm all three triggers exist.
- Re-save each trigger to refresh auth tokens.
- Run each script manually once.
- Confirm execution logs are successful.

1. Drive contract validation

- Verify these still exist and are writable:
  - `00_INBOX`
  - `01_CANDIDATES`
  - `90_ARCHIVE`
  - `91_SYSTEM`
  - `_DRIVE_INDEX`
- Confirm script constants and folder IDs still point to live folders.

1. Notion sync validation

- Verify Notion page `Google Drive Organization - Progress Tracker` is reachable.
- Add a new session log entry with restart timestamp.
- Confirm any downstream Notion updates from Make.com appear.

1. Post-restart hardening

- Add weekly health review to HEARTBEAT:
  - last_success timestamps for all scenarios
  - trigger enabled checks
  - connection auth checks

## Evidence used

- `Documents/Bryan's Vault/TODO.md` contains uncompleted config task for Make scenario manifest.
- `Documents/Bryan's Vault/config/` was empty before recovery.
- Notion search confirms tracker page exists and still shows last session around 2026-02-18.

## Definition of done

Mark workflow resumed only when all are true:

- Make.com scenario run succeeded in the last 24h
- All 3 Apps Script jobs show successful execution in expected cadence
- `_DRIVE_INDEX` receives fresh updates
- Notion tracker has a new dated session entry and no active blockers

## Current blocker summary

- Remaining blocker is configuration-level, not auth-level:
  - Router filters in Make.com UI still need to be set to stop duplicate create/update path execution.
- Remaining validation is Google-hosted:
  - Apps Script installable trigger verification and test run logs.

## Make UI Failure Fallback (Observed 2026-03-06)

- Symptom: Make scenario page repeatedly throws an "orphans" JavaScript error and visual editor fails to load reliably.
- Impact: Router filters cannot be trusted via direct UI editing path.
- Fallback path: patch scenario blueprint by API and apply filters at downstream route modules.

Recommended router filter implementation:

- Create route module (`id: 6`): filter where `{{4.id}}` does not exist
- Update route module (`id: 7`): filter where `{{4.id}}` exists

Post-patch sequence:

1. Save blueprint patch
2. Reactivate scenario `4162531`
3. Run controlled test for both cases (new candidate vs existing candidate)
4. Confirm exactly one route executes per run

## Patch Status Update (Later 2026-03-06)

- Router filters were applied in blueprint and accepted (`isinvalid: false`).
- Router gating behavior appears correct from run history:
  - earlier run hit create path
  - later runs hit update path for duplicate case
- Additional production fixes were applied:
  - Update module mapper corrected (`updateBy`, `select`, `data_source`, `page`)
  - Notion property types remapped (`text` -> `rich_text`; `Phone` -> `rich_text`)
- Scenario reactivated and executions launched; final completion status still pending capture.

## Validation Results (Final - 2026-03-06)

- Validation executions completed successfully:
  - ~06:59:02, SUCCESS, 18 operations, ~35s
  - ~06:59:23, SUCCESS, 18 operations, ~41s
- Compared to pre-fix pattern:
  - prior failures were status error with ~5 operations
  - fixed version runs full ~18 operations and completes successfully
- Confirmed fixed in this session:
  - router init/orphan issue handled via API fallback
  - OpenAI rawText type mismatch fixed (`toString()` wrapper)
  - router filters placed correctly on downstream modules
  - Notion type mapping corrected to `rich_text`

Remaining known gap (hardening task):

- Module 4 Notion search currently lacks candidate-name query filtering and may return arbitrary records for duplicate checks.
- Execution checklist: `docs/plans/2026-03-06-module4-query-filter-hardening-checklist.md`
