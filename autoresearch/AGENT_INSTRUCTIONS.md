# Rapid Source Skill Optimizer

## Goal

Improve the pass rate of `prompts/current.md` (the rapid-source skill file) through an eval-driven optimization loop. The skill generates Boolean search strings and InMail templates for biotech/pharma executive recruiting. Your job is to make it perform better — measured quantitatively — without making it longer, harder to read, or brittle.

---

## Context

**What the skill does:** Bryan Blair (VP, GQR Global Markets) pastes a biotech job description into Claude. The skill instructs Claude to produce 3 LinkedIn Recruiter Boolean search strings, 2 InMail templates, and a follow-up message — immediately, without narration, calibrated to Bryan's voice.

**What the eval tests:** 15 realistic job descriptions across 7 biotech functions (clinical ops, drug safety/PV, biostatistics, CDM, clinical development, medical affairs, CMO). Each output is scored against 8 binary assertions. A test case only "passes" if ALL 8 assertions pass.

**The 8 assertions:**
1. `boolean_depth` — 3+ Boolean strings, each with 3+ OR clusters
2. `not_block` — every Boolean string has a NOT block for seniority exclusion
3. `client_anonymized` — InMails never name the client company
4. `word_count` — each InMail body is ≤120 words
5. `no_banned_phrases` — no banned phrases, em dashes, exclamation points, or "resume"
6. `impact_endings` — hook and CTA sentences end on high-weight words
7. `onsite_disclosure` — roles with 3+ days onsite disclose this in the InMail
8. `cro_logic` — CRO excluded for clinical ops, NOT excluded for PV/biometrics/CDM

**Test case distribution:**
- 3 Clinical Operations (CRA, CTM, Clinical Outsourcing) — CRO must be excluded
- 2 Drug Safety/PV — CRO must NOT be excluded
- 2 Biostatistics — CRO must NOT be excluded
- 2 CDM — CRO must NOT be excluded
- 2 Clinical Development (VP, Medical Director)
- 1 Medical Affairs (VP)
- 1 CMO/C-Suite
- 1 Regulatory Affairs
- 1 Contract CRA (speed-critical)

---

## Each Optimization Cycle

### Step 1: Run the eval

```bash
python evals/runner.py prompts/current.md
```

The runner prints a summary to stdout and writes full results to `results/latest_run.json`.

### Step 2: Analyze failures

Read `results/latest_run.json`. Focus on:
- Which assertion has the lowest pass rate?
- Which test case function/level/location combinations fail most?
- Is there a pattern (e.g., "cro_logic fails for all clinical_ops cases" or "word_count fails for c_suite roles")?

### Step 3: Write failure analysis

Append to `results/failure_analysis.txt`:

```
=== Cycle [N] — [date] ===
Baseline score: [X%]

Top failing assertion: [assertion_name] ([X/15] cases failing)
Failure pattern: [description — what do the failing cases have in common?]
Root cause hypothesis: [what in the current skill file is causing this?]
Proposed fix: [one-sentence description of the change you will make]
```

### Step 4: Make ONE change

Create `prompts/candidates/v[N].md` — a copy of `prompts/current.md` with your single targeted change.

Add a comment at the very top of the file:
```
<!-- Hypothesis: [what this change should fix and why] -->
<!-- Cycle: [N] | Baseline: [X%] -->
```

**What counts as ONE change:**
- Adding or clarifying a rule
- Rewording an existing rule for precision
- Adding an example to an existing rule
- Reordering a section for emphasis
- Adding a specific instruction about a case type (e.g., "For CDM roles, do NOT include CRO in the NOT block")

**What does NOT count:**
- Changing three rules at once ("a few small tweaks")
- Adding a new section AND rewriting an old one
- Deleting a rule (never delete — only add or reword)

### Step 5: Evaluate the candidate

```bash
python evals/runner.py prompts/candidates/v[N].md
```

### Step 6: Compare and decide

**If candidate score > current score:**
1. Copy candidate to current:
   ```bash
   cp prompts/candidates/v[N].md prompts/current.md
   ```
2. Archive the previous version:
   ```bash
   cp prompts/history/previous.md prompts/history/v[N-1]_[old_score_pct].md
   ```
   (Use the score from before this cycle, e.g., `v2_67pct.md`)
3. Log the improvement (see Step 7)

**If candidate score ≤ current score:**
1. Do NOT replace current.md
2. Note the failed hypothesis in the log
3. Increment the "no improvement" counter

### Step 7: Log the cycle

Append to `results/optimization_log.md`:

```markdown
## Cycle [N] — [date]

| Field | Value |
|---|---|
| Hypothesis | [one sentence] |
| Score before | [X%] |
| Score after | [Y%] |
| Decision | Kept / Reverted |
| Notes | [anything interesting] |
```

---

## Control Logic

### Stopping conditions (stop when EITHER is met)

1. Overall pass rate exceeds **90%** — success, the skill is well-optimized
2. **20 cycles** completed — stop regardless of score

### Stuck handling

After **3 consecutive cycles with no improvement**, try a STRUCTURAL change instead of a rule tweak:
- Reorder sections (e.g., put the CRO logic rule higher up)
- Add concrete examples to the rule that keeps failing
- Change the output template to add an explicit checkpoint
- Add a per-function routing section (e.g., "For Clinical Ops roles, follow this checklist...")

### Per-assertion floor

No single assertion should drop below **70%** as a result of a change. If your candidate scores 80% overall but drops `cro_logic` from 80% to 60%, revert it — you've broken a specific behavior while fixing another.

---

## Quality Constraints

The skill file must remain:
- **Under 250 lines** — brevity is part of the skill's quality
- **Readable by Bryan** — plain English, no jargon specific to ML optimization
- **Action-oriented** — rules should tell Claude what TO do, not just what to avoid
- **Self-consistent** — no rules should contradict each other

---

## Reading `latest_run.json`

Key fields to look at:

```json
{
  "summary": {
    "overall_pass_rate": 0.67,
    "per_assertion_pass_rates": {
      "boolean_depth": 0.93,
      "cro_logic": 0.53,
      ...
    }
  },
  "failure_analysis": {
    "top_failing_assertions": [["cro_logic", 7], ["word_count", 3], ...],
    "failures_by_assertion": {
      "cro_logic": ["tc_001", "tc_002", "tc_015"]
    },
    "failures_by_function": {
      "clinical_ops": {"cro_logic": ["tc_001", "tc_002"]}
    }
  }
}
```

Use `failures_by_function` and `failures_by_level` to understand patterns. The runner also saves timestamped copies in `results/` for historical comparison.

---

## Final Deliverable

When the loop ends (either by hitting 90% or 20 cycles), `prompts/current.md` is the optimized skill file. `results/optimization_log.md` is the audit trail of what worked and what didn't.
