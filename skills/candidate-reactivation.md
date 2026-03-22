---
name: candidate-reactivation
description: "Surface reactivation candidates from Notion pipeline. Use when Bryan says 'reactivate', 'who fits this', 'mine the database', 'candidate match', 'who's available', 'who have we talked to', 'anyone in the pipeline for [role]', or 'stale candidates.' Also trigger when Bryan provides a JD and asks who he's already spoken to that might fit. This skill MUST be read before any reactivation query."
---

# Candidate Reactivation

## Purpose

Query the Notion Candidate DB to surface candidates worth re-engaging — either matched against a new JD (Mode A) or flagged as stale pipeline needing attention (Mode B). Output is a ranked, actionable list Bryan can work from immediately.

---

## CRITICAL RULES

### Rule 1: No Narration

Do not explain your query logic. Do not print status labels. Deliver the ranked list.

### Rule 2: Never Contact Blocked Statuses

These statuses are DO NOT CONTACT:
- **Not Interested** — candidate explicitly declined. Respect it.
- **Withdrew** — candidate pulled out of process. Do not re-engage unless Bryan overrides.

These statuses CAN be reactivated:
- **Active** — currently in pipeline, may need follow-up
- **New Lead** — captured but not fully engaged
- **Archive - Past Contact** — prior relationship exists, eligible for reactivation if role fit is strong
- **Submitted** — was submitted somewhere, check if that process concluded
- **Interviewing** — may still be in play or process may have died

### Rule 3: Tiered Staleness Thresholds

Do NOT use a flat 60-day threshold. Use this logic:

| Tier | Condition | Threshold |
|---|---|---|
| **Hot** | Candidate was in active process when a role closed (rejected, role filled, company paused) | 30 days since last contact |
| **Warm** | General active pipeline — status is Active or New Lead | 60 days since last contact |
| **Cool** | Archive - Past Contact with prior GQR relationship | 90 days since last contact |

Candidates who fall below their tier threshold are "stale" and surface in Mode B.

### Rule 4: Recency Weights Matching

In Mode A (JD Match), when ranking candidates:
- **Contact recency** matters. A strong-fit candidate contacted last week ranks above an equally strong-fit candidate from four months ago — the recent one is actionable today.
- **Scoring formula:** Match Strength (0-10) x Recency Multiplier
  - Last 14 days: x 1.5
  - 15-30 days: x 1.2
  - 31-60 days: x 1.0
  - 61-90 days: x 0.8
  - 90+ days: x 0.6

### Rule 5: Explain the Match

For Mode A, every candidate must have a WHY. "Therapeutic area overlap" is not enough. "8 years in oncology Phase III clinical operations at sponsor-side biotechs, with specific CRO oversight experience matching the JD's vendor management requirement" is a match explanation.

### Rule 6: Show Days, Not Dates

"Last contact: 47 days ago" — not "Last contact: January 30, 2026." Days since contact is immediately actionable. Dates require math.

---

## Notion Source

**Database:** Candidate DB (data source ID: 3841a478-62d3-4e5d-8265-d429375bd314)

Query this database using Notion MCP. If Notion MCP is unavailable, flag: "Notion connection required for reactivation queries. Connect Notion MCP and retry."

---

## Mode A: JD Match

### Input
Bryan provides a JD (pasted or uploaded) and says some variant of "who fits this" or "anyone in the pipeline."

### Execution

1. Parse the JD for key matching criteria: functional area, therapeutic area, seniority level, specific skills/platforms, location requirements
2. Query Notion Candidate DB for candidates matching those criteria
3. Filter out blocked statuses (Rule 2)
4. Score each candidate: Match Strength x Recency Multiplier (Rule 4)
5. Rank by composite score, descending

### Output

```
REACTIVATION MATCHES: [Role Title] at [Company]
Searched: [X] candidates in Notion DB
Matches found: [Y]

| Rank | Candidate | Last Status | Days Since Contact | Match Score | Match Reason | Suggested Action |
|------|-----------|-------------|-------------------|-------------|--------------|-----------------|
| 1 | [Name] | [Status] | [X days] | [Score] | [Specific match explanation — Rule 5] | [Call / InMail / Email + specific talking point] |
| 2 | ... | ... | ... | ... | ... | ... |
```

**Suggested Action** should be specific:
- "Call — was interested in similar role at [prior company], process died when role was filled internally. Lead with the [specific differentiator] of this new opportunity."
- "InMail — Archive contact from 4 months ago. Re-engage with: 'We spoke about [prior role]. A similar opportunity just opened at a [stage] [TA] biotech.'"
- "Email — Active candidate, just submitted to [other company]. Cross-submit if no exclusivity conflict."

### If No Matches Found

"No pipeline matches for this JD. Recommended action: Run rapid-source [role title] for fresh sourcing."

---

## Mode B: Stale Pipeline Review

### Input
No JD. Bryan says "stale candidates," "who needs follow-up," or this runs automatically on Monday mornings.

### Execution

1. Query Notion Candidate DB for all candidates in Active, New Lead, Submitted, or Interviewing status
2. Apply tiered thresholds (Rule 3) to identify stale candidates
3. Group by company/role where applicable
4. For each stale candidate, suggest a reactivation approach

### Output

```
STALE PIPELINE REVIEW — [Date]
Candidates reviewed: [X]
Stale candidates found: [Y]

## HOT (30+ days — process died, candidate may still be available)

| Candidate | Last Status | Company/Role | Days Since Contact | Suggested Action |
|-----------|-------------|-------------|-------------------|-----------------|
| [Name] | [Status] | [Company - Role] | [X days] | [Specific reactivation approach] |

## WARM (60+ days — general pipeline gone quiet)

| Candidate | Last Status | Company/Role | Days Since Contact | Suggested Action |
|-----------|-------------|-------------|-------------------|-----------------|
| ... | ... | ... | ... | ... |

## COOL (90+ days — archive candidates worth reconnecting)

| Candidate | Last Status | Company/Role | Days Since Contact | Suggested Action |
|-----------|-------------|-------------|-------------------|-----------------|
| ... | ... | ... | ... | ... |
```

### If Pipeline Is Current

"Pipeline is current — no stale candidates above threshold. [X] candidates in active status, all contacted within their tier window."

---

## Scheduled Task: Monday Morning Stale Review

**Cron:** `45 8 * * 1` (Monday, 8:45 AM)

Runs Mode B automatically. Delivers the stale pipeline review without Bryan asking. If no stale candidates found, reports: "Pipeline is current — no reactivation needed this week."

---

## Output Mode Toggle

**Full Report:** Default. Complete tables with all columns.

**Quick List:** If Bryan says "quick" or "just names" — deliver candidate names, days since contact, and suggested action only. Skip match scores and detailed reasoning.

---

## Next Skill Suggestions

- "Found a match? → Run: interview-prep [candidate] for [role]"
- "Need to submit? → Run: candidate-submission [candidate] for [company]"
- "No matches? → Run: rapid-source [role title] for fresh candidates"
- "Candidate placed? → Log in placement-metrics.xlsx"

---

## What This Skill Is NOT

- Not a sourcing tool. This mines existing relationships, not new ones. For new candidates, use rapid-source.
- Not a CRM. Notion is the CRM. This skill reads from it.
- Not a mass outreach system. Each reactivation is a one-to-one, context-specific re-engagement.
- Not a place to guess. If candidate notes are thin, say "limited context in Notion — review notes before calling" rather than fabricating a reactivation angle.
