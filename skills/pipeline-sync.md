---
name: pipeline-sync
description: Cross-reference pipeline audit for Bryan Blair's biotech recruiting operation. Compares Notion (Pipeline Snapshot + Active Searches + Candidates), recent chat history, and memory to detect drift, status mismatches, and phantom momentum. Produces a discrepancy report, applies Bryan-confirmed fixes to Notion, and surfaces remaining gaps. Use this skill whenever Bryan says "pipeline check", "pipeline sync", "pipeline fix", "sync my pipeline", "reconcile pipeline", "pipeline integrity", "is my pipeline accurate", "clean up Notion", "pipeline reset", or any variation. Also triggers pre-Nicole (before weekly 1-on-1 prep) and when things "feel off." This skill MUST be read before any sync execution — do not attempt from memory or from CLAUDE.md specs.
---

# Pipeline Sync

## Purpose

Cross-reference Notion pipeline data against chat history and memory context. Detect drift, apply confirmed corrections, surface gaps. Output: a discrepancy report for Bryan's review, then confirmed fixes pushed to Notion.

---

## CRITICAL RULES — Read Before Executing

These rules exist because Claude Code has failed on every one of them. They are non-negotiable.

### Rule 1: Write to Disk, Not to Context

Every stage produces a markdown file in `~/pipeline-sync/`. Context compaction WILL destroy in-memory work mid-sync. Files survive compaction.

```
~/pipeline-sync/
├── meta.md                  # Date, trigger context, MCP status
├── stage1_notion.md         # Active Searches + Candidates snapshot from Notion
├── stage1_chats.md          # Pipeline-relevant activity from chat history + memory
├── stage2_discrepancies.md  # Cross-reference results — THE deliverable
├── stage3_confirmed.md      # Bryan's confirmed fixes (subset of stage2)
├── stage3_sync_log.md       # Every Notion update with timestamps + old/new values
└── stage3_gaps.md           # Remaining gaps, blind spots, process health
```

**Before starting Stage 2, confirm `stage1_notion.md` and `stage1_chats.md` exist on disk and contain data. If either is empty or missing, re-run Stage 1. Do NOT proceed from memory.**

### Rule 2: No Narration

Do not print phase labels, status tables, confidence scores, or progress updates between steps. Execute silently. The only outputs Bryan sees are:

1. The Discrepancy Report (Stage 2 — for correction)
2. The Sync Log (Stage 3 — confirmation of what changed)
3. The Gap List (Stage 3 — what remains unresolved)

No "Phase 2: Cross-Reference Analysis." No "HIGH confidence." No emoji. Just the deliverables.

### Rule 3: Never Invent Pipeline State

If you cannot confirm a status from Notion, chat history, or memory — write "UNCONFIRMED — needs Bryan's input" in the stage file. Do NOT guess:

- Candidate statuses
- Interview outcomes
- Submission dates
- Next steps
- Whether something is active or dead

### Rule 4: Dead Stays Dead

Before flagging ANY candidate, search, or submission as "stale" or "missing activity":

1. Check Bryan's memory/context for that candidate + company
2. Search past conversations if needed
3. If Bryan has previously said it's dead, closed, on hold, or archived — it stays dead

Stale Notion data does NOT mean a live gap. Bryan's spoken word overrides database timestamps.

### Rule 5: Bryan's Word Overrides Everything

When Bryan corrects the discrepancy report:

- Apply the correction immediately
- Do not argue, explain, or qualify
- His live correction IS the source of truth
- Update `stage3_confirmed.md` with exactly what he said

### Rule 6: Pin the Date

First line of `meta.md`:

```
Today: [Day of week], [Month] [Day], [Year]
Trigger: [trigger_context value]
Scope: [scope value]
Lookback: [lookback_days] days
```

Reference this file whenever writing dates. Do not calculate days of the week from memory.

### Rule 7: Notion MCP Is Required — Degrade Gracefully If Missing

This skill depends on Notion MCP tools. If Notion MCP is disconnected:

1. Log it in `meta.md`
2. Proceed with chat-history-only analysis for Stage 1
3. In Stage 2, flag all Notion-sourced comparisons as "NOTION UNAVAILABLE — chat/memory only"
4. In Stage 3, write intended updates to `stage3_sync_log.md` as "QUEUED — Notion disconnected" instead of executing them

---

## Inputs

| Variable | Type | Required | Default |
|----------|------|----------|---------|
| trigger_context | string | optional | "weekly check" |
| scope | string | optional | "all" (all active searches) |
| lookback_days | number | optional | 7 |

---

## Execution

### Pre-Flight (30 seconds)

1. Create `~/pipeline-sync/` directory (wipe if exists from prior run)
2. Write `meta.md` with today's date, trigger context, scope, lookback days, and Notion MCP connection status
3. Confirm Notion MCP is connected by running a test search
4. If Notion MCP is disconnected: log it, proceed in degraded mode (see Rule 7)

### Stage 1: Gather

**Goal:** Pull current pipeline state from all sources into structured files on disk.

#### 1A: Notion Pull

1. Fetch Active Searches DB — filter to Status = Active or On Hold
   - Use `notion-query-database-view` with Active Searches default view
   - Capture: Role Title, Client (company), Status, Priority, Fee Structure, Last Activity Date, Candidates count
2. For each active search, fetch linked Candidates
   - Capture: Candidate Name, Current Status, Last Contact, Next Follow-Up, Current Company, Current Title
3. Fetch the Pipeline Snapshot page content (if it exists)
   - Capture: Last Updated date, current snapshot content
4. Write everything to `stage1_notion.md` in structured format:
   ```
   ## ACTIVE SEARCHES (from Notion)

   ### [Company] — [Role Title]
   - Status: [status] | Priority: [priority] | Fee: [fee structure]
   - Last Activity: [date]
   - Candidates:
     - [Name] | Status: [status] | Last Contact: [date] | Next Follow-Up: [date]

   ## PIPELINE SNAPSHOT (current Notion page)
   Last Updated: [date]
   [snapshot content]
   ```

**Fallback:** If Notion MCP fails, write "NOTION UNAVAILABLE" to `stage1_notion.md` and proceed to 1B.

#### 1B: Chat History + Memory Pull

1. Pull chat history from the last [lookback_days] days
2. Scan for pipeline-relevant activity:
   - Candidate status changes mentioned in conversation
   - New searches discussed
   - Searches closed or put on hold
   - Submissions made
   - Interview feedback received
   - Offers extended or rejected
   - Bryan's verbal corrections to pipeline state
3. Review memory context (MEMORY.md, any relevant memory files) for:
   - Account statuses
   - Known dead processes
   - Commission splits
   - Recent decisions
4. Write to `stage1_chats.md`:
   ```
   ## CHAT HISTORY — Last [N] days

   ### [Date] — [Summary of pipeline-relevant activity]
   - [Specific detail with source reference]

   ## MEMORY CONTEXT
   - [Relevant memory entries]
   ```

**Fallback:** If no relevant chat history found, write "NO PIPELINE ACTIVITY IN CHAT HISTORY — last [N] days" and proceed.

#### Stage 1 Checkpoint

Before proceeding to Stage 2:

```bash
# Verify both files exist and have content
wc -l ~/pipeline-sync/stage1_notion.md ~/pipeline-sync/stage1_chats.md
```

If either file is under 3 lines, something failed. Re-run the failing substage.

### Stage 2: Cross-Reference

**Goal:** Compare all sources, detect discrepancies, produce a report for Bryan's review.

1. Read `stage1_notion.md` and `stage1_chats.md` from disk (not from memory)
2. For each active search and candidate, compare:
   - **Status mismatches:** Notion says "Screening" but chat says "Submitted to Client"
   - **Missing entries:** Candidate discussed in chat but not in Notion (or vice versa)
   - **Phantom momentum:** Notion shows "Active" but no activity in lookback window and no chat mentions
   - **Stale next steps:** Next Follow-Up date has passed with no recorded activity
   - **Date conflicts:** Last Contact in Notion doesn't match most recent email/chat activity
3. For each discrepancy found, classify as:
   - `STATUS_MISMATCH` — Notion status differs from chat/memory evidence
   - `MISSING_IN_NOTION` — activity exists in chat but no Notion record
   - `MISSING_IN_CHAT` — Notion record exists but zero recent activity (check Rule 4 before flagging)
   - `STALE_NEXT_STEP` — follow-up date passed, no recorded action
   - `DATE_CONFLICT` — timestamps don't align across sources
   - `SNAPSHOT_DRIFT` — Pipeline Snapshot page content doesn't match current DB state
4. Write to `stage2_discrepancies.md` using this format:

```markdown
# PIPELINE DISCREPANCY REPORT — [Date]

Sources checked: Notion Active Searches, Notion Candidates, Pipeline Snapshot page, [N]-day chat history, memory context

## Discrepancies Found: [count]

| # | Type | Search/Candidate | Notion Says | Chat/Memory Says | Recommended Fix |
|---|------|-----------------|-------------|-----------------|-----------------|
| 1 | STATUS_MISMATCH | [Name] at [Company - Role] | [Notion value] | [Chat/memory value] | [Proposed action] |
| 2 | MISSING_IN_NOTION | [Name] | — | [What chat says] | Create Notion record |

## No Issues Detected
[List searches/candidates that checked out clean — one line each]

## Pipeline Snapshot Status
- Last updated: [date from Notion]
- Drift detected: [yes/no]
- [If yes: specific differences]
```

5. Present the discrepancy report to Bryan. Say: "Discrepancy report ready. What needs fixing?"
6. **STOP and wait for Bryan's corrections before proceeding to Stage 3.**

This is a deliberate gate. The report IS the Stage 2 deliverable. Bryan's response triggers Stage 3.

### Stage 3: Fix & Sync

**Goal:** Apply Bryan-confirmed fixes to Notion, regenerate Pipeline Snapshot, surface remaining gaps.

Only execute AFTER Bryan confirms or corrects the discrepancy report.

#### 3A: Apply Fixes

1. Write Bryan's confirmed corrections to `stage3_confirmed.md`:
   ```
   ## CONFIRMED FIXES

   | # | Discrepancy | Bryan's Decision | Action |
   |---|-------------|-----------------|--------|
   | 1 | [from stage2] | [what Bryan said] | [exact Notion update] |
   ```
2. For each confirmed fix, execute the Notion update:
   - Use `notion-update-page` for status changes, date updates, field modifications
   - Use `notion-create-pages` for missing records Bryan wants added
3. Log every update to `stage3_sync_log.md`:
   ```
   ## SYNC LOG — [Date]

   | Timestamp | Record Type | Name | Field | Old Value | New Value | Source |
   |-----------|-------------|------|-------|-----------|-----------|--------|
   | [time] | Candidate | [name] | Status | Screening | Submitted | Bryan confirmed |
   ```

**Validation:** Every entry in `stage3_sync_log.md` MUST have a corresponding entry in `stage3_confirmed.md`. No unconfirmed updates.

#### 3B: Regenerate Pipeline Snapshot

1. Query Active Searches DB again (post-fix state)
2. Rebuild the Pipeline Snapshot page content using the eod-sweep snapshot template format
3. Update the Pipeline Snapshot page via Notion MCP
4. Set "Last Updated" to today's date

#### 3C: Surface Gaps

1. Write `stage3_gaps.md`:

```markdown
# REMAINING GAPS — [Date]

## Follow-Ups Needed
| Search/Candidate | Gap | Suggested Action |
|-----------------|-----|-----------------|
| [Name] | [What's missing] | [What Bryan should do] |

## Blind Spots
- [Areas with no data in any source]

## Process Health
| Metric | Count |
|--------|-------|
| Total Active Searches | [n] |
| Searches with activity in last [lookback] days | [n] |
| Searches with NO activity in last [lookback] days | [n] |
| Candidates with overdue follow-ups | [n] |
| Pipeline Snapshot age before this sync | [n] days |
```

2. Present `stage3_gaps.md` as the final deliverable.

---

## Error Handling

| Problem | Response |
|---------|----------|
| Notion MCP disconnected | Proceed chat-history-only. Queue intended updates in sync log as "QUEUED." |
| Context compaction during sync | Read files back from `~/pipeline-sync/`. Resume from the last completed stage file. |
| Active Searches DB returns empty | Log as anomaly in meta.md. Check if DB ID changed. Ask Bryan before proceeding. |
| Candidate record has no status | Write "NO STATUS SET" — do not guess. Flag in discrepancy report. |
| Bryan corrects something | Apply immediately. Do not argue or explain why you got it wrong. |
| Chat history unavailable | Proceed with Notion-only analysis. Note reduced coverage in discrepancy report header. |

---

## What This Skill Is NOT

- Not a daily email scanner. That's eod-sweep. This audits cumulative drift.
- Not an intelligence report. No signal analysis or market commentary.
- Not a narration exercise. No phase labels, progress bars, or confidence scores.
- Not autonomous. Stage 3 executes ONLY after Bryan confirms fixes. No unsanctioned Notion writes.
- It is a reconciliation tool. Gather, compare, report, confirm, fix. That's it.
