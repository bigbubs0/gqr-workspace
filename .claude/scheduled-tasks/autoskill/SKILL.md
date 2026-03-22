---
name: autoskill
description: Use when Bryan says "autoskill", "skill audit", "skill sweep", "improve skills", or asks to run the autonomous skill improvement loop. Also use for the scheduled autoskill pass that discovers local skills, scores them, applies one isolated edit at a time, and keeps or reverts changes based on measured score delta.
---

# Autoskill

## Purpose

Run a fixed-budget, autoresearch-style improvement loop for Bryan-owned skills. Use deterministic scripts for discovery, scoring, backups, logging, and registry sync. Use the agent only for the actual SKILL.md prose edit.

## Guardrails

- Mutate only Bryan-owned Claude skills and Claude scheduled tasks.
- Discover `.codex` and `.agents` skills, but treat them as audit-only.
- Exclude `autoskill`, `.system`, `vendor_imports`, and any system-managed path from autonomous edits.
- Preserve behavioral logic. Improve wording, structure, references, and metadata only.
- Make one isolated edit per experiment.
- Keep an edit only if the re-scored dimension is strictly higher.
- Revert immediately on equal or worse score.
- Write all run state to `~/.claude/skill-improvement/`.
- Read this skill from disk before running. Do not execute from memory.

## Required References

Read these files before starting the loop:

- `references/home-registry.json`
- `references/rubric.md`
- `references/registry-sync.md`

## Script Entry Points

Use the Python CLI in `scripts/autoskill.py`.

Core commands:

```powershell
python scripts/autoskill.py init-run --budget-minutes 30
python scripts/autoskill.py start-experiment --run-tag <run-tag>
python scripts/autoskill.py evaluate-change --run-tag <run-tag> --change-note "<what changed>"
python scripts/autoskill.py sync-registry --run-tag <run-tag>
python scripts/autoskill.py finalize-run --run-tag <run-tag>
```

Optional inspection commands:

```powershell
python scripts/autoskill.py discover
python scripts/autoskill.py score-skill --skill-path <path-to-skill>
```

## Run Protocol

### 1. Initialize the run

Run:

```powershell
python scripts/autoskill.py init-run --budget-minutes 30
```

This command must:
- create a run tag in the form `autoskill-YYYYMMDD-HHMM`
- discover all configured skill homes
- baseline-score every discovered skill once
- write `manifest.json`, `inventory.md`, and `baseline.tsv`
- create global logs if they do not exist

### 2. Loop until the budget expires

Repeat this cycle until the manifest deadline is reached:

1. Run:

   ```powershell
   python scripts/autoskill.py start-experiment --run-tag <run-tag>
   ```

2. Read the returned target skill and lowest-scoring dimension.
3. Edit only that one skill and only for that one dimension.
4. Run:

   ```powershell
   python scripts/autoskill.py evaluate-change --run-tag <run-tag> --change-note "<what changed>"
   ```

5. Accept the script decision:
   - `improved` -> keep the edit
   - `unchanged` -> reverted automatically
   - `reverted` -> reverted automatically

Do not batch edits. Do not manually override the keep or revert decision.

### 3. Sync the Claude registry

After the loop ends, run:

```powershell
python scripts/autoskill.py sync-registry --run-tag <run-tag>
```

This updates `C:\Users\BryanBlair\CLAUDE.md` for Claude-owned skills only. Audit-only homes emit warnings instead of edits.

### 4. Finalize the run

Run:

```powershell
python scripts/autoskill.py finalize-run --run-tag <run-tag>
```

This writes `summary.md`, appends `changelog.md`, updates the manifest, and prints the one-line completion summary.

## Edit Policy

- Prefer the smallest change that can raise the target score.
- Fix encoding artifacts and mojibake when they hurt readability.
- Improve triggers, structure, and reference hygiene before chasing stylistic polish.
- If a dimension cannot be improved without changing behavior, leave the file alone and log the failed attempt through `evaluate-change`.

## Failure Handling

- If discovery finds zero eligible Claude targets, finalize the run with an error summary and stop.
- If a script raises an error, fix the script first. Do not continue with manual bookkeeping.
- If the active experiment file is missing, do not guess prior state. Start a new experiment.
- If a backup is missing, do not edit the target skill. Re-run `start-experiment`.
- If `CLAUDE.md` cannot be parsed, log a sync warning and continue to finalization.
