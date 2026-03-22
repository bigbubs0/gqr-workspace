# EOD Sweep Execution Patterns

## Architecture (Updated 3/9/26)
3-stage bookkeeping tool. Not a gap detection system or intelligence report.
- Stage 1: Scan (Inbox + Sent) - write to ~/sweep/ stage files
- Stage 2: Build Snapshot - present for Bryan's correction
- Stage 3: Sync + Draft - only after Bryan confirms

## Critical Rules (Baked into SKILL.md)
- Write to disk (`~/sweep/`), not context - compaction WILL destroy in-memory work
- No narration - no phase labels, confidence scores, or progress updates
- Never invent candidate details - UNREADABLE if can't read, never guess
- Never escalate dead processes - Bryan's spoken word overrides DB timestamps
- Pin the date in meta.md - don't calculate days of week from memory

## Lessons Learned (3/9/26 - First Full Sweep)

### Candidate Name Accuracy
Double-check ALL candidate names against source data. Misspellings (Marten vs Martin) and wrong attributions (Suresh vs Tony Tang) were caught by Bryan. New SKILL.md enforces validation pass: grep stage files for every name in snapshot.

### Pipeline Snapshot
- Bryan prefers concise, structured format with clear sections
- Include: Active roles by client, BD initiatives, active candidates, dead/archive, tomorrow priorities
- Day of week matters - get it right (reference meta.md)
- Company sections ordered by activity level (most active first)

### Email Drafts
- Mode 2 (Client Relationship) for external emails to recruiters/clients
- Keep drafts short and direct - no flowery language
- Always flag To field for manual verification due to autocomplete limitation
- One draft at a time, fully complete before starting next

### Timing
- Browser automation is the bottleneck (Comet viewport issues, element finding)
- Notion operations are fast and reliable
- ~/sweep/ files survive context compaction - always read from disk between stages
