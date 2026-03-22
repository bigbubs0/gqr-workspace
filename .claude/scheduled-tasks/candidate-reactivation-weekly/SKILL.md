---
name: candidate-reactivation-weekly
description: Use when the Monday 8:45 AM scheduled task fires or Bryan says 'reactivation weekly', 'stale pipeline', or 'Monday review'. Queries Notion Candidate DB for candidates exceeding tier thresholds (Hot: 30d, Warm: 60d, Cool: 90d) and surfaces them grouped by tier. Runs candidate-reactivation skill in Mode B.
---

Run the candidate-reactivation skill in Mode B (Stale Pipeline Review). Query the Notion Candidate DB for candidates in Active, New Lead, Submitted, or Interviewing status whose Last Contact exceeds their tier threshold (Hot: 30 days, Warm: 60 days, Cool: 90 days). Present the stale pipeline review grouped by tier. Follow the skill at ~/.claude/skills/candidate-reactivation/SKILL.md exactly.

## Error Handling

- **Notion query fails or times out:** Do not guess at pipeline state. Log the failure, report it to Bryan, and stop. Never fabricate candidate data.
- **candidate-reactivation skill missing:** Verify the skill exists at `~/.claude/skills/candidate-reactivation/SKILL.md` before proceeding. If absent, halt and notify Bryan.
- **No stale candidates found:** This is a valid result. Report "No candidates exceed tier thresholds" and exit cleanly. Do not invent urgency.

## Guardrails

- Never send outreach messages. Surface candidates for Bryan's review only.
- Do not modify Notion records during this task. Read only.
- Confirm Last Contact dates are present before applying tier thresholds. Candidates with missing dates should be flagged, not silently skipped.