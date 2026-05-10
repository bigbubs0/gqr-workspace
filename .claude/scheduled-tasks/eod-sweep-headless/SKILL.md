---
name: eod-sweep-headless
description: Headless wrapper for the eod-sweep skill. Runs daily M-F at 6:00 PM ET via Windows Task Scheduler. Calls /preflight then /eod-sweep, stops at Stage 3 awaiting Bryan's review (does NOT auto-confirm Stage 4). Logs to ~/.claude/run-log.jsonl, escalates via Windows toast on preflight FAIL or non-zero exit.
---

# eod-sweep-headless (scheduled task)

This is **not** a Claude-invoked skill — it's a Windows-Task-Scheduler entry that runs on its own. Bryan does not call this. The task scheduler does, via `run.ps1`.

## What it does

1. Calls `claude -p "/preflight then /eod-sweep"` with a 25-minute timeout
2. Parses the preflight verdict from output:
   - `Status: GO` → preflight passed, sweep proceeds
   - `Status: BLOCKED` → escalates via toast + writes `_escalations/` file, sweep does NOT run
3. The existing `eod-sweep` skill writes stage files to `~/sweep/` and **stops at Stage 3 for Bryan's review** — the headless wrapper respects that. No Notion writeback happens autonomously.
4. Logs every run to `~/.claude/run-log.jsonl`

## Why headless

Top friction in /insights report: pipeline workflows stalled on environmental dependencies (Notion MCP not connected, §9 stale, etc.) discovered mid-session. By moving the dependency check to a daily cron, blockers surface as toasts in the morning instead of as a wasted 30 minutes of Bryan's evening.

## What it does NOT do

- Does **not** auto-confirm Stage 4 (Notion writeback or email drafts). Bryan reviews the snapshot and confirms manually. Aligns with `feedback_no_unsolicited_email_drafts.md`.
- Does **not** modify program.md §9. That stays under `program-sync` skill control.
- Does **not** run on weekends — Mon–Fri only (matches Bryan's working pattern).

## Files

- `run.ps1` — entry point invoked by Task Scheduler. Dot-sources `_lib/run-headless.ps1`.

## Schedule

- Trigger: Daily 6:00 PM America/New_York
- Day mask: Mon, Tue, Wed, Thu, Fri
- Action: `pwsh -File C:\Users\bblai\.claude\scheduled-tasks\eod-sweep-headless\run.ps1`
- Registered via: `~/.claude/scheduled-tasks/_lib/Register-DailyRunners.ps1` (COM API)

## Operator notes

- To dry-run: `pwsh -File run.ps1 -DryRun`
- To inspect last run: `Get-Content C:\Users\bblai\.claude\run-log.jsonl -Tail 5 | ConvertFrom-Json | Where-Object { $_.task -eq 'eod-sweep-headless' }`
- Escalations land in `~/.claude/scheduled-tasks/_escalations/`
