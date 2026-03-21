#!/usr/bin/env python3
"""
runner.py — Rapid Source Skill Evaluation Harness

Uses Claude Code CLI (your Claude Max subscription) instead of API keys.

Usage:
    python evals/runner.py prompts/current.md
    python evals/runner.py prompts/current.md --verbose
    python evals/runner.py prompts/candidates/v3.md --verbose
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Resolve project root (parent of evals/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = PROJECT_ROOT / 'evals'
RESULTS_DIR = PROJECT_ROOT / 'results'
TEST_CASES_PATH = EVALS_DIR / 'test_cases.jsonl'

# Add evals directory to path so we can import assertions
sys.path.insert(0, str(EVALS_DIR))
from assertions import ASSERTIONS, ASSERTION_NAMES, run_all_assertions, all_pass  # noqa: E402


# ---------------------------------------------------------------------------
# Claude Code CLI call
# ---------------------------------------------------------------------------

def call_claude(
    system_prompt: str,
    user_message: str,
    retries: int = 3,
    retry_delay: float = 5.0,
) -> Optional[str]:
    """
    Call Claude via the Claude Code CLI using Bryan's Max subscription.
    Uses 'claude -p' (print mode) which sends a single prompt and returns output.
    No API key needed - uses the authenticated Claude Code session.
    """
    # Build the full prompt: system context + user input
    full_prompt = f"""You are executing a skill file. Follow the instructions in the skill exactly. Here is the skill:

---SKILL FILE START---
{system_prompt}
---SKILL FILE END---

Now execute the skill for this input. Output ONLY the skill's deliverables (Boolean strings, InMails, follow-up, sourcing notes). No preamble, no commentary.

INPUT:
{user_message}"""

    for attempt in range(1, retries + 1):
        try:
            result = subprocess.run(
                ['claude', '-p', full_prompt, '--output-format', 'text'],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout per generation
                cwd=str(PROJECT_ROOT),
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            # If claude CLI returned an error
            if result.stderr:
                error_msg = result.stderr.strip()[:200]
                if attempt < retries:
                    wait = retry_delay * attempt
                    print(f"\n    [Attempt {attempt}/{retries}] CLI error: {error_msg}. Retrying in {wait:.0f}s...")
                    time.sleep(wait)
                else:
                    print(f"\n    [Attempt {attempt}/{retries}] CLI error: {error_msg}. Giving up.")
                    return None
            elif not result.stdout.strip():
                if attempt < retries:
                    wait = retry_delay * attempt
                    print(f"\n    [Attempt {attempt}/{retries}] Empty response. Retrying in {wait:.0f}s...")
                    time.sleep(wait)
                else:
                    print(f"\n    [Attempt {attempt}/{retries}] Empty response. Giving up.")
                    return None

        except subprocess.TimeoutExpired:
            if attempt < retries:
                print(f"\n    [Attempt {attempt}/{retries}] Timeout. Retrying...")
            else:
                print(f"\n    [Attempt {attempt}/{retries}] Timeout. Giving up.")
                return None

        except FileNotFoundError:
            print("\nERROR: 'claude' CLI not found. Install Claude Code:")
            print("  npm install -g @anthropic-ai/claude-code")
            sys.exit(1)

        except Exception as e:
            if attempt < retries:
                wait = retry_delay * attempt
                print(f"\n    [Attempt {attempt}/{retries}] {type(e).__name__}: {e}. Retrying in {wait:.0f}s...")
                time.sleep(wait)
            else:
                print(f"\n    [Attempt {attempt}/{retries}] {type(e).__name__}: {e}. Giving up.")
                return None

    return None


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------

def load_skill_file(skill_path: Path) -> str:
    if not skill_path.exists():
        print(f"ERROR: Skill file not found: {skill_path}")
        sys.exit(1)
    return skill_path.read_text(encoding='utf-8')


def load_test_cases() -> List[Dict]:
    if not TEST_CASES_PATH.exists():
        print(f"ERROR: Test cases not found: {TEST_CASES_PATH}")
        sys.exit(1)
    cases = []
    with open(TEST_CASES_PATH, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"WARNING: Skipping malformed test case on line {line_num}: {e}")
    return cases


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_output(output: str, metadata: Dict) -> Dict[str, bool]:
    """Run all assertions and return per-assertion pass/fail dict."""
    return run_all_assertions(output, metadata)


def compute_summary(all_results: List[Dict]) -> Dict[str, Any]:
    n = len(all_results)
    if n == 0:
        return {}

    assertion_pass_counts = {name: 0 for name in ASSERTION_NAMES}
    overall_pass_count = 0

    for result in all_results:
        scores = result.get('assertion_scores', {})
        case_passed = all(scores.get(name, False) for name in ASSERTION_NAMES)
        if case_passed:
            overall_pass_count += 1
        for name in ASSERTION_NAMES:
            if scores.get(name, False):
                assertion_pass_counts[name] += 1

    per_assertion_rates = {
        name: round(assertion_pass_counts[name] / n, 4)
        for name in ASSERTION_NAMES
    }

    return {
        'total_cases': n,
        'overall_pass_count': overall_pass_count,
        'overall_pass_rate': round(overall_pass_count / n, 4),
        'per_assertion_pass_rates': per_assertion_rates,
        'per_assertion_pass_counts': assertion_pass_counts,
    }


# ---------------------------------------------------------------------------
# Failure pattern analysis
# ---------------------------------------------------------------------------

def analyze_failures(all_results: List[Dict]) -> Dict[str, Any]:
    failures_by_assertion = {name: [] for name in ASSERTION_NAMES}
    failures_by_function = {}
    failures_by_level = {}

    for result in all_results:
        scores = result.get('assertion_scores', {})
        metadata = result.get('metadata', {})
        tc_id = result.get('id', 'unknown')

        fn = metadata.get('function', 'unknown')
        level = metadata.get('level', 'unknown')

        for name in ASSERTION_NAMES:
            if not scores.get(name, False):
                failures_by_assertion[name].append(tc_id)
                failures_by_function.setdefault(fn, {}).setdefault(name, []).append(tc_id)
                failures_by_level.setdefault(level, {}).setdefault(name, []).append(tc_id)

    sorted_failures = sorted(
        [(name, len(ids)) for name, ids in failures_by_assertion.items()],
        key=lambda x: x[1],
        reverse=True
    )

    return {
        'top_failing_assertions': sorted_failures,
        'failures_by_assertion': {k: v for k, v in failures_by_assertion.items() if v},
        'failures_by_function': failures_by_function,
        'failures_by_level': failures_by_level,
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def print_summary(skill_path: Path, summary: Dict, failure_analysis: Dict, verbose_results: List[Dict] = None):
    sep = '-' * 60
    print(f"\n{sep}")
    print(f"RAPID SOURCE SKILL EVAL RESULTS")
    print(f"Skill file : {skill_path}")
    print(f"Engine     : Claude Code CLI (Max subscription)")
    print(f"Timestamp  : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(sep)

    overall_rate = summary.get('overall_pass_rate', 0)
    n_pass = summary.get('overall_pass_count', 0)
    n_total = summary.get('total_cases', 0)
    print(f"\nOVERALL PASS RATE: {overall_rate:.1%}  ({n_pass}/{n_total} test cases pass ALL assertions)\n")

    print("PER-ASSERTION PASS RATES:")
    per_rates = summary.get('per_assertion_pass_rates', {})
    per_counts = summary.get('per_assertion_pass_counts', {})
    for name in ASSERTION_NAMES:
        rate = per_rates.get(name, 0)
        count = per_counts.get(name, 0)
        bar_fill = int(rate * 20)
        bar = '#' * bar_fill + '.' * (20 - bar_fill)
        flag = ' !!' if rate < 0.70 else ''
        print(f"  {name:<25} [{bar}] {rate:.0%} ({count}/{n_total}){flag}")

    top_failures = failure_analysis.get('top_failing_assertions', [])
    if top_failures and top_failures[0][1] > 0:
        print(f"\nTOP FAILURE PATTERNS:")
        for name, count in top_failures[:3]:
            if count == 0:
                break
            print(f"  {name}: fails on {count}/{n_total} cases")
            failing_ids = failure_analysis.get('failures_by_assertion', {}).get(name, [])
            if failing_ids:
                print(f"    Cases: {', '.join(failing_ids)}")

    if verbose_results:
        print(f"\nPER-TEST-CASE RESULTS:")
        header = f"  {'ID':<12} {'ALL':<5} " + ' '.join(f"{n[:8]:<8}" for n in ASSERTION_NAMES)
        print(header)
        for result in verbose_results:
            tc_id = result.get('id', 'unknown')
            scores = result.get('assertion_scores', {})
            passed_all = all(scores.get(n, False) for n in ASSERTION_NAMES)
            all_str = 'PASS' if passed_all else 'FAIL'
            score_str = ' '.join(f"{'PASS':<8}" if scores.get(n, False) else f"{'FAIL':<8}" for n in ASSERTION_NAMES)
            print(f"  {tc_id:<12} {all_str:<5} {score_str}")

    print(f"\n{sep}")
    print(f"Results saved to: results/latest_run.json")
    print(sep)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Evaluate a rapid-source skill file against test cases using Claude Code CLI.'
    )
    parser.add_argument(
        'skill_file',
        type=Path,
        help='Path to the skill .md file (e.g. prompts/current.md)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print per-test-case assertion results and include full output in JSON'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without calling Claude — useful for testing the harness'
    )
    args = parser.parse_args()

    skill_path = args.skill_file
    if not skill_path.is_absolute():
        skill_path = PROJECT_ROOT / skill_path

    skill_content = load_skill_file(skill_path)
    test_cases = load_test_cases()

    # Verify Claude Code is available (unless dry run)
    if not args.dry_run:
        try:
            check = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=10)
            if check.returncode != 0:
                print("ERROR: Claude Code CLI not working properly.")
                print("Make sure you're logged in: claude login")
                sys.exit(1)
            print(f"Claude Code: {check.stdout.strip()}")
        except FileNotFoundError:
            print("ERROR: 'claude' CLI not found.")
            print("Install: npm install -g @anthropic-ai/claude-code")
            sys.exit(1)

    print(f"Loaded {len(test_cases)} test cases")
    print(f"Evaluating: {skill_path.name}")

    if args.dry_run:
        print("DRY RUN MODE: Claude calls skipped; outputs will be empty.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    all_results = []

    for i, test_case in enumerate(test_cases, 1):
        tc_id = test_case.get('id', f'tc_{i:03d}')
        user_input = test_case.get('input', '')
        metadata = test_case.get('metadata', {})

        fn = metadata.get('function', 'unknown')
        level = metadata.get('level', 'unknown')

        print(f"  [{i:02d}/{len(test_cases)}] {tc_id} ({fn}/{level})...", end='', flush=True)

        if args.dry_run:
            output = ''
        else:
            output = call_claude(
                system_prompt=skill_content,
                user_message=user_input,
            )
            # Brief pause between calls
            time.sleep(1)

        if output is None:
            print(' ERROR')
            output = ''

        assertion_scores = score_output(output, metadata)
        passed_all = all_pass(assertion_scores)
        status = 'PASS' if passed_all else 'FAIL'
        print(f' {status}')

        result = {
            'id': tc_id,
            'metadata': metadata,
            'assertion_scores': assertion_scores,
            'passed_all': passed_all,
            'output_length': len(output),
            'output_word_count': len(output.split()),
        }

        if args.verbose:
            result['output'] = output

        all_results.append(result)

    summary = compute_summary(all_results)
    failure_analysis = analyze_failures(all_results)

    run_results = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'skill_file': str(skill_path.name),
        'engine': 'claude-code-cli',
        'summary': summary,
        'failure_analysis': failure_analysis,
        'test_results': all_results,
    }

    latest_path = RESULTS_DIR / 'latest_run.json'
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(run_results, f, indent=2, default=str)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    skill_stem = skill_path.stem
    archive_path = RESULTS_DIR / f'run_{ts}_{skill_stem}.json'
    with open(archive_path, 'w', encoding='utf-8') as f:
        json.dump(run_results, f, indent=2, default=str)

    verbose_data = all_results if args.verbose else None
    print_summary(skill_path, summary, failure_analysis, verbose_data)

    pass_rate = summary.get('overall_pass_rate', 0)
    sys.exit(0 if pass_rate >= 0.90 else 1)


if __name__ == '__main__':
    main()
