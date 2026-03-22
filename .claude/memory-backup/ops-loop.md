---
name: ops-loop
description: Trigger words and workflow for recruiting ops improvement loop - bug logging, one-fix-per-session discipline
type: feedback
---

When Bryan says "ops loop", "bug log", or "fix mode":
1. Load `~/Documents/recruiting-ops/program.md`
2. Show open bugs sorted by frequency (3x same failure = escalated)
3. Ask which one to fix this session

**Why:** Ad-hoc fixes don't stick. The same failure mode recurs 2 weeks later because the fix wasn't tracked, tested, or committed systematically.

**How to apply:**
- **Logging:** When Bryan says `log: <description>`, append to the Bug Log table in program.md with today's date and status `open`. Confirm with one line.
- **Fix workflow:** Read the relevant SKILL.md, find the exact line(s) that caused the failure, propose the smallest diff. Bryan runs the skill once to eyeball. He says "commit" or "revert." Commit message format: `fix(skill-name): description`.
- **Escalation:** If the same failure appears 3x in the bug log, stop patching - escalate to architecture review.
- **Discipline:** One fix per session. Never stack a second fix on top of a broken first fix. Never rewrite a whole skill to fix one bug.
