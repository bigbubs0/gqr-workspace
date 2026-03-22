---
name: context-refresh-monthly
description: Use when the monthly scheduled task fires or Bryan says 'monthly context refresh', 'context sync', or 'update operational reality'. Reviews conversations from the last 30 days, diffs against operational_reality.json, and presents changes for approval. Runs context-refresh skill in monthly mode.
---

Run the context-refresh skill in monthly mode. Execute the operational reality refresh: pull recent conversations from the last 30 days, build a diff against operational_reality.json, and present changes for Bryan's approval. Follow the skill at ~/.claude/skills/context-refresh/SKILL.md exactly.

## Error Handling

If the context-refresh skill file is missing or unreadable, stop and report the path that failed — do not proceed from memory. If conversation history is unavailable, note the gap and present whatever data is accessible for Bryan's review.