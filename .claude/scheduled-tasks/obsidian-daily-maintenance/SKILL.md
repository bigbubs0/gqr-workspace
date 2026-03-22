---
name: obsidian-daily-maintenance
description: Use when running the daily Obsidian vault maintenance pass. Processes inbox files, checks TODO.md for urgent or overdue items, flags stale pipeline candidates, and writes a session summary to memory/.
---

You are maintaining Bryan Blair's Obsidian vault at:
C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\

This is the DAILY maintenance pass from HEARTBEAT.md. Execute each step:

## Path Anchor

Treat these as the canonical filesystem targets for this task:

- Vault root: `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault`
- Inbox: `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\inbox`
- TODO: `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\TODO.md`
- Candidate folder: `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\candidates`
- Company folder: `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\companies`
- Search folder: `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\searches`
- Memory output: `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\memory\YYYY-MM-DD.md`
- Heartbeat file: `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\HEARTBEAT.md`

## 1. Check /inbox/ for new files
- Read the contents of `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\inbox`
- If files exist (CVs, JDs, voice notes, articles), list them and move to appropriate locations:
  - CVs -> `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\candidates`
  - JDs -> `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\searches`
  - Other files -> flag in TODO.md as needing manual triage
- If inbox is empty, note "Inbox clear" in the session summary

## 2. Check TODO.md for URGENT items
- Read `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\TODO.md`
- If any items are in the URGENT section, flag them prominently in the session summary
- Check if any completed items (marked [x]) should be removed or archived
- Check if dates on any Active items have passed (overdue)

## 3. Check for stale pipeline activity
- Read files in `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\candidates` and `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\recruiting\companies`
- Flag any files not modified in >7 days that appear to be active (not archived)

## 4. Write session summary
- Create a new file at `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\memory\YYYY-MM-DD.md` using today's date
- Format:
```
# Session Summary - YYYY-MM-DD (Daily Auto)

## Inbox
- [processed/empty status]

## Urgent Items
- [any urgent TODOs or "None"]

## Stale Flags
- [files needing attention or "None"]

## Notes
- Automated daily maintenance pass
```

## 5. Update HEARTBEAT.md
- Use `C:\Users\BryanBlair\OneDrive - GQR Global Markets\Documents\Bryan's Vault\HEARTBEAT.md`
- Do NOT modify the checklist template
- This task counts as the "every session" pass being executed

## Important context:
- Bryan's CLAUDE.md is at `C:\Users\BryanBlair\CLAUDE.md` - read it for voice/style if writing any notes
- The vault syncs via OneDrive - files are written directly to the filesystem
- Bryan has dyslexia and uses voice-to-text - never flag typos in any content you encounter
- Use hyphens, never em dashes
- Be concise and direct in all written output

## Error Handling

| Problem | Response |
|---------|----------|
| Inbox directory doesn't exist | Create it. Log "Created inbox/" in session summary. |
| TODO.md missing or unreadable | Log "TODO.md not found - skipping TODO check" in session summary. Continue with other steps. |
| File move fails (permissions, OneDrive sync lock) | Leave file in inbox. Flag in TODO.md: "[MANUAL] Move failed for {filename} - retry needed". |
| Vault path unreachable | Stop execution. Print: "Vault not accessible at expected path. Check OneDrive sync status." |
| memory/ directory doesn't exist | Create it before writing session summary. |
| Stale file check finds too many results (>20) | Report first 20. Note "Additional stale files exist - consider bulk archive." |
