# rapid-source Autoresearch Package

Overnight eval-driven optimization loop for Bryan Blair's `rapid-source` recruiting skill. Clone onto a Lambda instance, run setup, and let Claude Code optimize the skill file while you sleep.

---

## What This Is

The `rapid-source` skill (at `prompts/current.md`) tells Claude how to generate Boolean search strings and InMail templates from a biotech/pharma job description. It covers Bryan's full desk: VP Clinical Development, Drug Safety/PV, Biostatistics, CDM, CMO, Medical Directors, CRAs, and contractors.

This package contains:
- **15 test JDs** covering 7 biotech functions and multiple seniority levels
- **8 binary assertions** that check the skill's output for correctness (Boolean depth, NOT blocks, client anonymization, word count, banned phrases, impact endings, onsite disclosure, CRO logic)
- **An evaluation harness** that scores any version of the skill file automatically
- **Agent instructions** for Claude Code to run a closed-loop optimization: eval → diagnose → hypothesize → edit → re-eval → keep or revert → repeat

---

## Prerequisites

1. **Lambda instance** — A1, A10, or equivalent. The eval calls the Anthropic API 15 times per cycle; minimal compute required.
2. **Python 3.8+** — Pre-installed on Lambda instances.
3. **Anthropic API key** — `claude-sonnet-4-5` for evals, `claude-opus-4` (via Claude Code) for optimization.
4. **Claude Code** — The `claude` CLI. Install via the [Anthropic docs](https://docs.anthropic.com/en/docs/claude-code). Required for the overnight loop; not required to run evals manually.

---

## Quick Start

Three commands after SSH-ing into your Lambda instance:

```bash
# 1. Clone the repo
git clone <your-repo-url> autoresearch && cd autoresearch

# 2. Set your API key and run setup (installs deps, runs baseline eval)
export ANTHROPIC_API_KEY=sk-ant-...
bash setup.sh

# 3. Start the overnight optimization loop
claude --dangerously-skip-permissions \
  'Follow AGENT_INSTRUCTIONS.md and run the full optimization loop'
```

Setup takes about 3 minutes (baseline eval makes 15 API calls). The overnight loop runs up to 20 optimization cycles and stops when pass rate exceeds 90% or cycles are exhausted.

---

## How It Works

### Eval loop (per cycle)

```
prompts/current.md
       │
       ▼
  runner.py  ──►  15 API calls  ──►  score 8 assertions per output
       │
       ▼
results/latest_run.json
       │
       ▼
  Claude Code reads failure patterns
       │
       ▼
  ONE targeted edit → prompts/candidates/vN.md
       │
       ▼
  runner.py on candidate
       │
       ├── better score? → copy to current.md, archive old
       └── worse/same?  → discard, try different approach
```

Each cycle is logged to `results/optimization_log.md`.

### The 8 assertions

| Assertion | What it checks |
|---|---|
| `boolean_depth` | 3 Boolean strings, each with 3+ OR clusters |
| `not_block` | Every Boolean string has a NOT block for seniority exclusion |
| `client_anonymized` | InMails never name the client company |
| `word_count` | Each InMail body ≤ 120 words |
| `no_banned_phrases` | No banned phrases, em dashes, exclamation points, or "resume" |
| `impact_endings` | Hook and CTA sentences end on strong words |
| `onsite_disclosure` | Roles with 3+ days onsite say so in the InMail |
| `cro_logic` | CRO excluded for clinical ops; NOT excluded for PV/biostats/CDM |

A test case **only passes** if all 8 assertions pass.

---

## Monitoring Progress

From a second terminal on the Lambda instance:

```bash
# Watch the optimization log update in real time
tail -f results/optimization_log.md

# Check current score
python3 evals/runner.py prompts/current.md

# See full results from last run
cat results/latest_run.json | python3 -m json.tool | grep -A5 '"summary"'
```

---

## Getting Results

When the loop completes, `prompts/current.md` is the optimized skill file. Copy it back to your workstation:

```bash
# From your local machine
scp ubuntu@<lambda-ip>:~/autoresearch/prompts/current.md ./rapid-source-optimized.md
```

Or review `results/optimization_log.md` for the full change history before deploying.

---

## Manual Eval (without Claude Code)

To run evals manually, cycle by cycle:

```bash
# Score current skill file
python3 evals/runner.py prompts/current.md --verbose

# Score a candidate variant
python3 evals/runner.py prompts/candidates/v3.md --verbose

# Dry run (no API calls, tests the harness)
python3 evals/runner.py prompts/current.md --dry-run
```

---

## File Structure

```
autoresearch-package/
├── README.md                    ← You are here
├── AGENT_INSTRUCTIONS.md        ← Claude Code's operating instructions
├── setup.sh                     ← One-command Lambda setup
├── prompts/
│   ├── current.md               ← Active skill file (edit target)
│   ├── history/                 ← Archived previous versions
│   └── candidates/              ← Candidate variants under evaluation
├── evals/
│   ├── test_cases.jsonl         ← 15 test JDs
│   ├── assertions.py            ← 8 binary assertion functions
│   └── runner.py                ← Evaluation harness
└── results/
    ├── latest_run.json          ← Most recent eval results
    ├── optimization_log.md      ← Cycle-by-cycle log (written by Claude Code)
    └── failure_analysis.txt     ← Per-cycle failure diagnosis
```

---

## Cost Estimate

| Component | Cost |
|---|---|
| Baseline eval (15 API calls) | ~$0.15 |
| Per optimization cycle (15 calls for eval + ~5 calls for Claude Code reasoning) | ~$0.25-0.40 |
| 20 cycles overnight | ~$5-8 total |

The runner uses `claude-sonnet-4-5` for evals (cost-efficient). Claude Code uses its own model for reasoning. Total overnight cost should fall between **$3 and $8** depending on output verbosity and how many Claude Code reasoning turns are needed per cycle.

---

## Customizing Test Cases

To add or modify test cases, edit `evals/test_cases.jsonl`. Each line is a JSON object:

```json
{
  "id": "tc_016",
  "input": "[paste the full JD here]",
  "metadata": {
    "function": "clinical_ops",
    "level": "director",
    "location_type": "hybrid",
    "contract_type": "perm",
    "onsite_days": 3
  }
}
```

Valid values:
- `function`: `clinical_ops`, `drug_safety_pv`, `biometrics`, `cdm`, `clinical_dev`, `medical_affairs`, `cmo`
- `level`: `associate`, `manager`, `director`, `senior_director`, `vp`, `svp`, `c_suite`
- `location_type`: `remote`, `hybrid`, `onsite`
- `contract_type`: `perm`, `contract`
- `onsite_days`: integer 0-5

---

## Troubleshooting

**`anthropic` module not found:**
```bash
pip install anthropic
```

**Rate limit errors during eval:**
The runner has retry logic with exponential backoff. If you hit sustained rate limits, add `--delay 2` (coming in a future version) or run during off-peak hours.

**Score stuck below 70%:**
Read `results/failure_analysis.txt` to see which assertions are failing. The most common root causes are `cro_logic` (the CRO exclusion rule is ambiguous in the skill file) and `word_count` (InMails running long on complex senior-level roles). Both are fixable with targeted rule additions.

**Claude Code loop exits early:**
Check `results/optimization_log.md` for the last cycle's notes. If Claude Code hit the 90% target, that's success. If it exited for another reason, re-run with:
```bash
claude 'Read AGENT_INSTRUCTIONS.md and results/optimization_log.md. Continue the optimization loop from the last completed cycle.'
```
