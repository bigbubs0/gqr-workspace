---
name: obsidian-weekly-audit
description: Use when running the Monday morning weekly vault audit. Covers job order summary, stale pipeline flags, Notion signal scans (funding, layoffs), clinical intelligence, archive review, sync health, account status, and TODO refresh.
---

You are running Bryan Blair's WEEKLY Monday audit on his Obsidian vault at:
`C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault`

This is the full HEARTBEAT.md weekly checklist. Execute every step:

## 1. Active Job Orders Summary
- Read files in `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\searches\` and `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\companies\`
- Summarize active job orders by status (sourcing, submitted, interviewing, offer, closed)
- Write summary to the weekly audit report

## 2. Stale Pipeline Flag
- Check `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\candidates\` for any candidate files with no modification in >7 days
- Flag them in the audit report with last-modified date

## 3. Notion Signal Scans (if Notion MCP available)
- Search Notion for recent entries in funding databases - flag Series B+ ($30M+) at biotech companies
- Search Notion for recent layoff entries - flag talent availability for active searches
- If Notion MCP calls fail, note "Notion auth expired - flag for Bryan" and continue

## 4. Clinical Intelligence
- Check for any notes in vault about positive clinical data readouts at tracked companies
- Flag any Phase 2 to Phase 3 transitions mentioned in company files
- Check company files for new job postings at target companies (CMO, VP Clinical, Head PV, Director Biometrics)

## 5. Archive Review
- Check `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\companies\` for files that match archive trigger conditions:
  - No activity >30 days
  - Marked as "dead" in content
  - Role filled/closed
- Recommend files for move to `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\90_archive\`

## 6. Company Core Updates
- If any new intelligence surfaced during checks above, update the relevant company file in `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\companies\`

## 7. Green/Red Sync Audit
- Read `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\config\sync-manifest.json` for health rules
- Read `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\config\make-scenarios.json` for scenario state
- Generate a new audit report using the template at `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\review\weekly-sync-audit-template.md`
- Score each service (Make.com scenario, Apps Script triggers, E2E chain)
- Write the completed audit to `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\review\weekly-sync-audit-YYYY-MM-DD.md`
- Overall status: GREEN only if ALL services GREEN, otherwise RED with blockers listed

## 8. USER.md Account Check
- Read `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\USER.md` and verify Active Accounts section is current
- Flag any accounts that appear stale or need status update
- Check if any Warm Leads have upcoming dates that need prep

## 9. TODO.md Refresh
- Update `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\TODO.md`:
  - Move completed items to a "## Recently Completed" section (keep last 2 weeks)
  - Add any new action items discovered during this audit
  - Flag anything that should be URGENT

## 10. Write Weekly Summary
- Create `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\memory\weekly-YYYY-MM-DD.md` with:
```
# Weekly Audit - YYYY-MM-DD

## Pipeline Status
[job orders summary]

## Stale Candidates (>7 days no activity)
[list or "None"]

## Signals Detected
[funding, layoffs, clinical data, job postings]

## Sync Health
[GREEN/RED + blockers]

## Account Status
[changes or "No changes"]

## Actions Generated
[new TODOs added]

## Archive Recommendations
[files to archive or "None"]
```

## Important context:
- Bryan's full config is at `C:\Users\BryanBlair\CLAUDE.md`
- Priority signals to flag immediately: Series B+ funding ($30M+), Phase 2->3 transitions, CMO/VP departures, FDA approvals, layoffs at competitors
- Bryan's accounts: Owned=Aditum. Team=Xellar, IDEAYA, Structure/Wave, Karyopharm. Warm=Regeneron (call 3/9).
- Use hyphens not em dashes. Be concise. Quantify everything.
- If any Notion or external API calls fail, log the failure and continue with what's available locally.

## Error Handling

| Problem | Response |
|---------|----------|
| Vault path unreachable | Stop execution. Print: "Vault not accessible - check OneDrive sync status." |
| Notion MCP auth expired | Log "Notion auth expired" in audit report. Skip Notion-dependent steps (3, 6). Continue with local data. |
| sync-manifest.json or make-scenarios.json missing | Skip step 7 (sync audit). Log "Config files missing - sync audit skipped" in report. |
| TODO.md missing | Create a fresh TODO.md with default sections. Log "Created new TODO.md" in audit. |
| memory/ directory doesn't exist | Create it before writing weekly summary. |
| >50 stale candidate files found | Report top 20 by staleness. Note "Additional stale files exist - consider bulk archive." |
| USER.md missing or unreadable | Skip step 8. Log "USER.md not found - account check skipped." |
