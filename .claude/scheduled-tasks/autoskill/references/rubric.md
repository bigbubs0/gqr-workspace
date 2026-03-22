# Autoskill Rubric

Six dimensions. Score each from 0 to 20. Total possible score: 120.

## Structure (0-20)

| Points | Criterion |
|--------|-----------|
| +4 | Valid frontmatter with `name` and `description` |
| +2 | `name` uses lowercase letters, digits, and hyphens only |
| +3 | Has `Overview` or `Purpose` |
| +3 | Triggers are present in the description or a body usage section |
| +3 | Has `Common Mistakes` or `Error Handling` |
| +3 | Word count stays under 3000 for skills or 1500 for scheduled tasks |
| +2 | Heading levels are consistent and do not jump erratically |

## CSO - Claude Skill Optimization (0-20)

| Points | Criterion |
|--------|-----------|
| +5 | Description starts with `Use when...` or `Use this skill when...` |
| +4 | Description avoids internal workflow narration |
| +3 | Description avoids first-person or second-person voice |
| +3 | Description stays under 500 characters |
| +3 | Description includes searchable trigger phrases or keywords |
| +2 | Description materially matches the body instructions |

## Prose (0-20)

| Points | Criterion |
|--------|-----------|
| +4 | Most representative sentences end on strong words |
| +3 | Adverbs and weak qualifiers are limited |
| +3 | Redundant filler phrases are limited |
| +2 | Weak openings like `There is`, `There are`, `It is`, `This is` are limited |
| +2 | Sentence lengths vary enough to avoid monotony |
| +4 | Sentences are economical and avoid obvious filler |
| +2 | Narrative text is free of mojibake or encoding artifacts such as `â`, `Ã`, `�`, or similar corruption |

## References (0-20)

| Points | Criterion |
|--------|-----------|
| +8 | Local filesystem paths mentioned by the skill resolve or are explicitly unverifiable placeholders |
| +6 | Cross-skill references resolve against known skill homes or are explicitly unverifiable placeholders |
| +6 | Command references use known commands or resolvable executables |

## CLAUDE.md Sync (0-20)

| Points | Criterion |
|--------|-----------|
| +10 | Claude-owned skill appears in `~/CLAUDE.md` skill table |
| +5 | Purpose text in the table materially matches the skill description |
| +5 | Status field uses a known value such as `Built`, `WIP`, or `Planned` |

For audit-only homes, do not attempt sync. Emit an audit warning instead.

## Error Handling (0-20)

| Points | Criterion |
|--------|-----------|
| +7 | At least one clear failure mode is documented |
| +7 | At least one fallback or continue path is documented |
| +6 | Guard rails are explicit: `Do not`, `Never`, `Confirm`, `Validate`, or `Verify` |

## Edit Rule

- Change only one dimension at a time.
- Preserve operational behavior.
- Keep an edit only if the targeted dimension rises strictly above its pre-edit score.
