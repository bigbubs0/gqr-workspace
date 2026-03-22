---
name: context-refresh-quarterly
description: Quarterly strategic profile refresh - full ICP, Voice DNA, Business Profile, and operational reality review
---

Run the context-refresh skill in quarterly mode. Execute the full strategic refresh: operational reality + ICP review + Voice DNA review + Business Profile review. Pull 90 days of conversations, build diffs, and present for Bryan's approval. Follow the skill at ~/.claude/skills/context-refresh/SKILL.md exactly.

## Error Handling

If the context-refresh skill file is missing or unreadable, stop and report the path that failed — do not proceed from memory. If any profile file (ICP, Voice DNA, Business Profile) is unavailable, note the gap and refresh the remaining profiles. If conversation history is insufficient, note the limitation and present what data is accessible for Bryan's review.