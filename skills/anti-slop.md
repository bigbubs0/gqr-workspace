---
name: anti-slop
description: "Post-processing filter that silently removes AI slop from content skill output. Not invoked directly - embedded as a critical rule in content-producing skills (interview-prep, client-discovery). Runs a 3-pass filter: kill list scan, compression, Voice DNA violation scan. Do not apply when sentence-editor is the primary invoking skill."
---

# Anti-Slop Filter

## Purpose

Post-processing filter that silently removes AI-generated slop from content skill output before it reaches Bryan. This skill is not invoked directly - it is embedded as a critical rule in content-producing skills.

**Do not apply when sentence-editor is the primary invoking skill.** Sentence-editor is a standalone editing tool; layering anti-slop on top creates circular filtering.

---

## Load Context

Before executing the filter, silently load:

1. **Kill List** - `kill-list.json` from this skill's directory
2. **Voice DNA v5.0** - Specifically: `never_sounds_like`, `ai_bloat_patterns_to_eliminate`, `business_jargon_replacements`, `search_and_replace_before_output`, `never` list

Do not reference these files. Use them silently.

---

## 3-Pass Filter Process

### Pass 1: Kill List Scan

Scan output against every entry in `kill-list.json`.

**Exact-match categories** (ai_tells, hedging, corporate_filler, bryan_specific_bans):
- Case-insensitive phrase matching
- If `replacement` is a string: swap the phrase for the replacement
- If `replacement` is null: delete the phrase
- After deletions: clean up orphaned punctuation, fix sentence flow, ensure grammatical correctness
- If deleting a phrase leaves an empty or nonsensical sentence, remove the entire sentence

**Pattern category** (bloat_patterns):
- These are LLM-evaluated using judgment, not regex-matched
- Read each pattern's `description` and `action` field
- Apply the prescribed action when the pattern is detected
- Use Bryan's preferred transitions (The reality:, What destroys me is, Look,, Meanwhile,) when replacing infomercial transitions

### Pass 2: Compression

Apply sentence-editor principles 3 (max economy) and 4 (never repeat) aggressively.

**Target:**
- Filler sentences that add no information
- Redundant qualifiers and restated points
- Hedging that weakens assertions without adding nuance
- Symmetrical sentence structures (a tell for AI-generated prose)

**Goal:** Zero unnecessary words, not a fixed percentage. For content that is already tight, the word count reduction may be minimal. For bloated first drafts, aim for ~25% reduction as a benchmark.

**Preserve:**
- All data points and specific numbers
- Technical terms and biotech jargon (IND, FDA, PK/PD, IDMC, DSMB, BLA/NDA, CMC, GCP, ICH-GCP, SAE)
- Bryan's signature transitions and fragment patterns
- Emotional hooks and confrontational openings (these are intentional, not bloat)

### Pass 3: Voice DNA Violation Scan

**Never Sounds Like check:**
Scan output against the 9 `never_sounds_like` categories. Does any paragraph read like:
- Motivational speaker (empty encouragement without tactical guidance)
- Corporate HR ("excited to embark on this journey")
- Academic researcher (passive voice, excessive hedging)
- Social justice activist (performative empathy without action)
- Tech bro optimizer ("10x your productivity")
- Therapy-speak practitioner ("I'm hearing that you feel...")
- Generic business consultant ("leveraging synergies")
- Humble-bragging influencer ("So grateful for this journey")
- Cold economic analyst (suppressed emotion)

If detected: rewrite the offending paragraph to match Bryan's voice - direct, data-driven, emotionally invested.

**Business jargon replacements:**
Apply all replacements from Voice DNA's `business_jargon_replacements`:
- leverages → uses
- encompasses → includes
- facilitates → enables
- utilized → used
- commenced → began
- wanted to → DELETE
- just checking → checking
- I think maybe → DELETE qualifiers
- managed to → DELETE "managed to"

These are the single source of truth for jargon swaps. Do not duplicate in the kill list.

**Search and replace:**
- Replace all em dashes (—) with hyphens (-)
- Replace all en dashes (–) with hyphens (-)

**Final authenticity check:**
Ask: "Would Bryan actually say this in this context?" If not, rewrite.

---

## Mode-Aware Exceptions

- **Modes 5 & 6** (candidate write-ups, CVs): Skip Pass 2 compression entirely. These modes are data-dense by design - every qualification matters. Passes 1 and 3 still run.
- **Mode 1** (thought leadership): All 3 passes run at full intensity. This is where slop is most visible.
- **Modes 2-4**: All 3 passes run normally.

---

## Output

Produce only the cleaned content. No diff, no violation report, no narration. Silent fix.

---

## What This Skill Is NOT

- Not a standalone skill to invoke manually
- Not a replacement for sentence-editor (sentence-editor refines prose; anti-slop catches AI tells)
- Not a Voice DNA modifier (reads from Voice DNA, never writes to it)
- Not applied to non-prose outputs (pipeline snapshots, ranked lists, diff reports)

---

## Maintenance

- **Kill list edits:** Bryan adds/removes phrases in `kill-list.json` anytime. Multi-word phrases only - single-word jargon stays in Voice DNA.
- **Voice DNA updates:** When Voice DNA is updated, review `bryan_specific_bans` category for additions or removals.
- **False positives:** If a kill-list phrase is flagged as a false positive in context, move it to `bloat_patterns` for judgment-based evaluation, or remove it entirely.
- **New content skills:** When candidate-submission, rapid-source, or other content skills are built, include the anti-slop critical rule.
