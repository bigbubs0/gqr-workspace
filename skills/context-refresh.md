---
name: context-refresh
description: "Use when Bryan says 'refresh context', 'update context profiles', 'context sync', or 'are my profiles current?' Also triggers on schedule. Runs monthly for operational reality (accounts, team, pipeline) and quarterly for strategic profiles (ICP, Voice DNA, Business Profile). This skill MUST be read before any context refresh."
---

# Context Profile Refresh

## Purpose

Keep Bryan's context files current by analyzing recent conversations, extracting changes, and presenting a pre-populated diff for Bryan's approval. Not a reminder to do work — it does the work.

---

## CRITICAL RULES

### Rule 1: No Narration

Do not print phase labels. Execute silently. The only output Bryan sees is the diff summary for approval.

### Rule 2: Never Overwrite Without Approval

Present all proposed changes as a diff. Bryan approves, rejects, or modifies before anything is written.

### Rule 3: Past Chats Are the Source of Truth

Pull the last 30 days (monthly) or 90 days (quarterly) of conversation history. Extract changes from actual conversations, not from memory assumptions.

### Rule 4: Distinguish Facts From Inferences

If a change is confirmed in a conversation (Bryan said "Ionis is dead"), mark as CONFIRMED. If inferred from patterns (no mentions of a client in 60 days), mark as [INFERRED — verify].

---

## Schedules

### Monthly: Operational Reality Refresh
**Cron:** `0 9 1 * *` (First of every month, 9:00 AM)
**Scope:** Team structure, active accounts, account classifications, commission structure, pipeline state

### Quarterly: Strategic Profile Refresh
**Cron:** `0 9 1 1,4,7,10 *` (First of Q1/Q2/Q3/Q4, 9:00 AM)
**Scope:** ICP personas, Voice DNA modes, Business Profile positioning — plus everything in the monthly scope

---

## Execution: Monthly Operational Refresh

### Step 1: Pull Recent Conversations

Use `recent_chats` and `conversation_search` to retrieve the last 30 days of conversations. Search for:

- Company names (new clients, dead accounts, status changes)
- "owned" / "team" / "split" / "commission" (account structure changes)
- Personnel names (new team members, departures, role changes)
- "dead" / "closed" / "on hold" / "killed" / "paused" (pipeline deaths)
- "new role" / "new account" / "BD" / "signed" (new business)
- "started" / "placed" / "offer accepted" (completed placements)

### Step 2: Build the Diff

Compare extracted data against current operational_reality.json. Produce a structured diff:

```
# OPERATIONAL REALITY DIFF — [Date]
## Review period: [Start date] → [Today]

### ACCOUNTS — CHANGES DETECTED

NEW ACCOUNTS:
- [Company] — [Classification: Owned/Team] — [Source: conversation date/link]

DEAD/PAUSED ACCOUNTS:
- [Company] — [Status: Dead/Paused/On Hold] — [Source: conversation date/link]

CLASSIFICATION CHANGES:
- [Company] — [Old classification] → [New classification] — [Source]

NO CHANGE (confirmed active):
- [List of accounts mentioned in recent conversations with no status change]

### TEAM — CHANGES DETECTED

[Any personnel changes, reporting structure shifts, new hires, departures]
Or: "No team changes detected in the last 30 days."

### COMMISSION/STRUCTURE — CHANGES DETECTED

[Any changes to split structures, account ownership, fee arrangements]
Or: "No structural changes detected."

### PIPELINE STATE — SUMMARY

Active roles by account: [Count per company]
Placements completed: [List with dates]
Candidates in process: [Count]

### ITEMS NEEDING BRYAN'S INPUT

1. [Specific question — e.g., "Is Puma Biotech still a BD target or has this gone cold?"]
2. [Specific question — e.g., "Aaron's split on Structure — still 60%?"]
```

### Step 3: Present and Wait

Show the diff to Bryan. Ask: "Here's what I found in the last 30 days. What needs correcting?"

**STOP. Do not update any files until Bryan confirms.**

### Step 4: Apply Updates

After Bryan confirms (with any corrections):

1. Update operational_reality.json with confirmed changes
2. Update `_meta.last_updated` timestamp
3. Log the update: what changed, what Bryan corrected, what was confirmed

---

## Execution: Quarterly Strategic Refresh

Run the full monthly operational refresh PLUS these additional steps:

### ICP Review

Search the last 90 days for:
- New hiring manager profiles or behaviors
- Candidate persona shifts (new objections, new motivations, market changes)
- Recruiting professional interactions (any changes to GQR's competitive landscape)

Present: "Any shifts to your typical hiring manager, candidate, or recruiting professional profiles since [last refresh date]?"

### Voice DNA Review

Search the last 90 days for:
- New communication patterns Bryan has developed
- Mode usage frequency (is he using Mode 4 more? Has Mode 6 emerged?)
- Any feedback on content voice or style

Present: "Any new communication modes or voice adjustments? Your LinkedIn content voice has [observation from recent posts] — should Voice DNA reflect this?"

### Business Profile Review

Search the last 90 days for:
- GQR positioning changes
- New service offerings or market focus
- Competitive landscape shifts

Present: "Any changes to how you're positioning GQR? New differentiators, service lines, or market focus?"

---

## Manual Trigger

If Bryan says "refresh context" or "update context profiles" outside the schedule:

1. Ask: "Full refresh (all profiles) or just operational reality?"
2. Execute the appropriate scope
3. Follow the same diff → approve → apply workflow

---

## Files This Skill Touches

| File | Monthly | Quarterly |
|---|---|---|
| operational_reality.json | Update | Update |
| icp.json | Skip | Review + Update |
| Voice DNA | Skip | Review only (Bryan updates manually) |
| Business Profile | Skip | Review + Update |

---

## What This Skill Is NOT

- Not a reminder. It does the research, builds the diff, and presents it for approval.
- Not an auto-updater. Bryan approves every change.
- Not a pipeline tracker. That's the EOD sweep. This is about context files that feed other skills.
