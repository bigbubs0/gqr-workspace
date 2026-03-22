---
name: eod-sweep
description: End-of-day pipeline sweep for Bryan Blair's biotech recruiting operation. Scans Outlook inbox and sent items, maps actions to pipeline, detects gaps, updates the Notion Pipeline Snapshot, and stages follow-up email drafts. Use this skill whenever Bryan says "EOD sweep", "end of day", "sweep", "pipeline update", "close out the day", or any variation. Also trigger when Bryan asks to sync his pipeline, check what happened today, or reconcile emails with Notion. This skill MUST be read before any sweep execution — do not attempt the sweep from memory or from CLAUDE.md specs.
---

# EOD Sweep

## Purpose

Scan Bryan's Outlook (inbox + sent), reconcile activity against the active pipeline, detect gaps, update Notion, and stage follow-up drafts. Output: a single corrected Pipeline Snapshot ready for Bryan's review.

---

## CRITICAL RULES — Read Before Executing

These rules exist because Claude Code has failed on every one of them. They are non-negotiable.

### Rule 1: Write to Disk, Not to Context

Every stage produces a markdown file in `~/sweep/`. Context compaction WILL destroy in-memory work mid-sweep. Files survive compaction.

```
~/sweep/
├── meta.md          # Date, time, browser status
├── stage1_inbox.md  # Every inbox email: sender, subject, timestamp, body summary
├── stage1_sent.md   # Every sent email: recipient, subject, timestamp, body summary
├── stage2_snapshot.md  # Draft pipeline snapshot
├── stage3_sync.md   # Notion update log
└── stage3_drafts.md # Email drafts staged or queued
```

**Before starting Stage 2, confirm `stage1_inbox.md` and `stage1_sent.md` exist on disk and contain data. If either is empty or missing, re-run Stage 1. Do NOT proceed from memory.**

### Rule 2: No Narration

Do not print phase labels, status tables, confidence scores, or progress updates between steps. Execute silently. The only output Bryan sees is:

1. The final Pipeline Snapshot (for correction)
2. A short list of Notion updates proposed
3. Draft emails (if browser is connected)

No "Phase 4: Gap Detection Report." No "MEDIUM confidence." No emoji. Just the deliverable.

### Rule 3: Never Invent Candidate Details

If you cannot read the full email body, write "UNREADABLE — manual review needed" in the stage file. Do NOT guess:

- Candidate names (especially from partial subject lines)
- Role titles
- Compensation figures
- Company names
- Interview outcomes

**After building the snapshot in Stage 2, re-read `stage1_inbox.md` and `stage1_sent.md` from disk. For every candidate name in the snapshot, confirm it appears verbatim in a stage file. If it does not, remove it and flag the gap.**

### Rule 4: Never Escalate Dead Processes

Before flagging ANY submission or process as "stale" or "at risk":

1. Check Bryan's memory/context for that candidate + company
2. Search past conversations if needed
3. If Bryan has previously said it's dead, closed, on hold, or archived — it stays dead

Stale Notion data from January does NOT mean a live gap. Bryan's spoken word overrides database timestamps.

### Rule 5: Read Every Email Fully

Do not skim subject lines. Open each recruiting-relevant email and read the body. Capture:

- Exact candidate name (spelled correctly)
- Exact role title
- Exact company
- Any compensation, interview dates, or status changes mentioned
- Who sent it and who received it

If the email won't open or the body won't load, log it as "FAILED TO READ" in the stage file with the subject line. Do not guess the contents.

### Rule 6: Pin the Date

First line of `meta.md`:

```
Today: [Day of week], [Month] [Day], [Year]
Tomorrow: [Day of week], [Month] [Day], [Year]
```

Reference this file whenever writing dates. Do not calculate days of the week from memory.

### Rule 7: You Are the Browser Operator — Never Delegate to Bryan

You have FULL control of the Perplexity Comet browser. You can click, scroll, type, navigate, and read the screen yourself.

NEVER ask Bryan to:

- Scroll down in the inbox or sent items
- Click into an email to read the body
- Switch between folders (Inbox → Sent Items)
- Open attachments
- Navigate to a different view or page
- "Show me" anything

If you need to see more emails below the fold — **scroll down yourself.**
If you need to read an email body — **click into it yourself.**
If you need Sent Items — **click the Sent Items folder yourself.**
If an email is partially visible — **scroll within the email yourself.**

You are the operator. Bryan is not your hands. Any response that asks Bryan to perform a browser action instead of performing it yourself is a **sweep failure**. If a browser action fails (element not found, page didn't load), retry once, then log as FAILED in the stage file and move on. Do not fall back to asking Bryan to do it for you.

---

## Execution

### Pre-Flight (30 seconds)

1. Create `~/sweep/` directory (wipe if exists from prior run)
2. Write `meta.md` with today's date, time, and browser connection status
3. Check browser/Comet connection — log status in `meta.md`
4. If browser is disconnected: log it, proceed with Notion-only stages, flag email drafts as BLOCKED at the end. Do NOT keep retrying the connection mid-sweep.

### Stage 1: Scan (Inbox + Sent)

**Goal:** Capture every recruiting-relevant email from today into structured files on disk.

#### 1A: Inbox Scan

1. Navigate to Outlook Inbox in Comet
2. Scroll through today's emails. For each recruiting-relevant email:
   - Click to open it
   - Read the full body
   - Write to `stage1_inbox.md`:
     ```
     ## [timestamp] — [sender]
     **Subject:** [exact subject]
     **Body summary:** [key details — candidate name, role, company, status, next steps]
     **Action needed:** [yes/no + what]
     ```
3. Skip newsletters, system notifications, and non-recruiting emails
4. When done, write `--- INBOX SCAN COMPLETE ---` at the bottom of the file

#### 1B: Sent Mail Scan

1. Navigate to Outlook Sent Items
2. Same process as inbox. For each sent email:
   - Click to open it
   - Read the full body
   - Write to `stage1_sent.md`:
     ```
     ## [timestamp] — To: [recipient]
     **Subject:** [exact subject]
     **Type:** [SUBMITTAL | CANDIDATE_UPDATE | CLIENT_FEEDBACK | BD_OUTREACH | MEETING | OTHER]
     **Body summary:** [key details]
     ```
3. For SourceWhale batch emails: log as a single entry with count and target company. Do not log each individual email.
4. When done, write `--- SENT SCAN COMPLETE ---` at the bottom of the file

#### Stage 1 Checkpoint

Before proceeding to Stage 2:

```bash
# Verify both files exist and have content
wc -l ~/sweep/stage1_inbox.md ~/sweep/stage1_sent.md
```

If either file is under 5 lines, something failed. Re-scan.

### Stage 2: Build Snapshot

**Goal:** Produce one clean Pipeline Snapshot document for Bryan's review.

1. Read `stage1_inbox.md` and `stage1_sent.md` from disk (not from memory)
2. Read Bryan's current memory context for active accounts, roles, candidates, and dead processes
3. Cross-reference emails against known pipeline to identify:
   - New roles or searches
   - Candidate status changes (submitted, interviewing, feedback received, offer, rejection)
   - Client communication updates (last contact dates)
   - BD activity (outbound campaigns, new targets)
4. Build the snapshot using Bryan's standard format (see Template below)
5. **Validation pass:** For every candidate name, role title, and company in the snapshot, grep `stage1_inbox.md` and `stage1_sent.md` to confirm the detail appears in an actual email. Remove anything that doesn't have a source.
6. Write to `stage2_snapshot.md`
7. Present to Bryan for correction. Say: "Here's today's snapshot. What needs fixing?"
8. **STOP and wait for Bryan's corrections before proceeding to Stage 3.**

### Stage 3: Sync + Draft

**Goal:** Push confirmed data to Notion and stage email drafts.

Only execute AFTER Bryan confirms or corrects the snapshot.

#### 3A: Notion Updates

1. Update the Pipeline Snapshot page with the corrected snapshot
2. Update candidate records (status changes, last contact dates)
3. Update Company Core records (last contact dates, new signals)
4. Log every update to `stage3_sync.md`:
   ```
   [timestamp] Updated [record type]: [name] — [field]: [old value] → [new value]
   ```

#### 3B: Email Drafts (Browser Required)

If browser is connected:

1. Identify emails that need to go out tomorrow based on the snapshot (follow-ups, scheduling requests, feedback forwarding)
2. Draft in Outlook as DRAFTS (do not send)
3. Log to `stage3_drafts.md`

If browser is disconnected:

1. Write the draft text to `stage3_drafts.md` with recipients and subject lines
2. Note: "BROWSER DISCONNECTED — drafts written to file, not staged in Outlook"

---

## Snapshot Template

Use this exact structure. Do not add sections Bryan hasn't asked for. Do not add confidence scores, BITA counts, intelligence notes, or signal analysis unless Bryan requests them.

```markdown
# PIPELINE SNAPSHOT — [Day], [Date]

## [COMPANY NAME] ([Account Type])
| Role | Status | Priority | Key Detail |
|------|--------|----------|------------|
| [Role Title] | [Status] | [Priority] | [One line of key context] |

## ACTIVE CANDIDATES
| Candidate | Company/Role | Status | Next Step |
|-----------|-------------|--------|-----------|
| [Name] | [Company - Role] | [Current status] | [What happens next] |

## DEAD / ARCHIVE
| Candidate | Company/Role | Reason |
|-----------|-------------|--------|
| [Name] | [Company - Role] | [Why it's dead] |

## [TOMORROW DAY] [DATE] PRIORITIES
1. [Priority item]
2. [Priority item]
...
```

**Formatting rules:**

- Company sections ordered by activity level (most active first)
- Account type in parentheses: Owned, Team (with split %), or BD Target
- Priority column only where meaningful — don't force-rank everything
- "Key Detail" is ONE line. Not a paragraph.
- Priorities list: actionable items only. No reminders Bryan doesn't need (he knows his own pipeline — trust him).
- Dead/Archive: only include items that moved to dead/archive TODAY. Don't resurface old dead processes.

---

## Error Handling

| Problem | Response |
|---------|----------|
| Browser disconnects mid-scan | Save whatever you captured to the stage file. Note where the scan stopped. Proceed with what you have. |
| Context compaction during sweep | Read files back from `~/sweep/`. Resume from the last completed stage file. |
| Email won't open | Log as FAILED TO READ with subject line. Move on. |
| Notion MCP fails | Log the intended update to `stage3_sync.md`. Bryan can push manually. |
| Candidate name unclear | Write exactly what you see. Add "[VERIFY]" tag. Do not guess. |
| Bryan corrects something | Apply the correction immediately. Do not argue or explain why you got it wrong. |

---

## What This Skill Is NOT

- Not a gap detection system. Bryan knows his pipeline. Don't alarm him.
- Not an intelligence report. No "signal inference" or "confidence scoring."
- Not a narration exercise. No phase labels, status tables, or progress updates.
- It is a bookkeeping tool. Scan, organize, present, correct, sync. That's it.
