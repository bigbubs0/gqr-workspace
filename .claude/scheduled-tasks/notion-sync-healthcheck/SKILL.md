---
name: notion-sync-healthcheck
description: Daily 8 AM ET headless preflight check. Verifies Notion MCP connectivity and program.md §9 freshness. Escalates via Windows toast on FAIL. Logs to ~/.claude/run-log.jsonl. WARN states log silently — only hard fails wake Bryan up.
---

# notion-sync-healthcheck (scheduled task)

Cheap morning check that surfaces broken dependencies before Bryan opens Claude Code for the day.

## What it does

1. Calls `claude -p "/preflight"` with a 5-minute timeout
2. Parses the preflight verdict:
   - `Notion MCP: PASS` + `§9 freshness: PASS` → silent log entry, no toast
   - `§9 freshness: WARN` (8–14 days stale) → log entry, no toast
   - `Notion MCP: FAIL` or `§9 freshness: FAIL` → toast + escalation file
3. Logs every run to `~/.claude/run-log.jsonl`

## Why this exists

Top recurring blocker in the /insights report: workflows stalled because Notion MCP wasn't connected in fresh worktree sessions, only discovered when `eod-sweep` failed mid-pull. This check catches that 10 hours before the 6 PM EOD sweep — Bryan has time to fix it before the day's heaviest pipeline workflow runs.

## What it does NOT do

- Does **not** restart MCP servers automatically. The toast points Bryan at the failure; he restarts.
- Does **not** trigger any sweep, Notion write, or email. Read-only health check.
- Does **not** push notifications when everything is fine — only failures escalate. Quiet success is the desired norm.

## Files

- `run.ps1` — entry point invoked by Task Scheduler. Dot-sources `_lib/run-headless.ps1`.

## Schedule

- Trigger: Daily 8:00 AM America/New_York
- Day mask: Mon, Tue, Wed, Thu, Fri (Bryan's working week)
- Action: `pwsh -File C:\Users\bblai\.claude\scheduled-tasks\notion-sync-healthcheck\run.ps1`
- Registered via: `~/.claude/scheduled-tasks/_lib/Register-DailyRunners.ps1`

## Operator notes

- To dry-run: `pwsh -File run.ps1 -DryRun`
- To force-fail (for verification): temporarily rename the Notion MCP entry, run, confirm toast fires, restore.
