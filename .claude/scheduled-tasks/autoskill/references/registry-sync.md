# Registry Sync Rules

Autoskill syncs only the Claude-owned registry at:

- `C:\Users\BryanBlair\CLAUDE.md`

## Scope

- Update rows for skills discovered under `~/.claude/skills`
- Update rows for scheduled tasks discovered under `~/.claude/scheduled-tasks`
- Do not edit `.codex` or `.agents` registries in v1

## Table Rules

- Target the table under `### Skills`
- Keep this column order:
  - `Skill`
  - `Status`
  - `Trigger`
  - `Purpose`
- If a discovered Claude-owned skill is missing, add a row with:
  - `Skill`: backticked skill name
  - `Status`: `Built`
  - `Trigger`: compact trigger summary from the frontmatter description
  - `Purpose`: compact purpose summary from the frontmatter description
- If a row exists, update only the `Purpose` field when it drifts materially
- Keep existing status values unless the row is newly created

## Audit Warnings

- For `.codex` and `.agents`, do not edit anything
- Record warnings in the run manifest and summary:
  - home discovered
  - number of skills found
  - registry edits skipped because the home is audit-only
