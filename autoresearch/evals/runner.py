#!/usr/bin/env python3
"""
runner.py — Rapid Source Skill Evaluation Harness

Usage:
    python evals/runner.py prompts/current.md
    python evals/runner.py prompts/current.md --verbose
    python evals/runner.py prompts/candidates/v3.md --verbose

Scores the given skill file against 15 test cases using 8 binary assertions.
Writes detailed results to results/latest_run.json.
Prints a summary to stdout.
"""

import argparse
import json
import os
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
# Anthropic client setup
# ---------------------------------------------------------------------------

def get_anthropic_client():
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Model and generation settings
# ---------------------------------------------------------------------------

MODEL = 'claude-sonnet-4-5'          # cost-efficient, strong instruction following
MAX_TOKENS = 4096                       # InMails + Booleans fit comfortably
TEMPERATURE = 0.3                       # low variance for consistent eval


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
# API call with retry
# ---------------------------------------------------------------------------

def call_claude(
    client,
    system_prompt: str,
    user_message: str,
    retries: int = 3,
    retry_delay: float = 5.0,
) -> Optional[str]:
    """
    Call the Claude API with retry logic.
    Returns the text content of the response, or None on failure.
    """
    for attempt in range(1, retries + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=system_prompt,
                messages=[{'role': 'user', 'content': user_message}],
            )
            return response.content[0].text
        except Exception as e:
            error_type = type(e).__name__
            if attempt < retries:
                wait = retry_delay * attempt
                print(f"    [Attempt {attempt}/{retries}] {error_type}: {e}. Retrying in {wait:.0f}s...")
                time.sleep(wait)
            else:
                print(f"    [Attempt {attempt}/{retries}] {error_type}: {e}. Giving up.")
                return None
    return None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_output(output: str, metadata: Dict) -> Dict[str, bool]:
    """Run all assertions and return per-assertion pass/fail dict."""
    return run_all_assertions(output, metadata)


def compute_summary(all_results: List[Dict]) -> Dict[str, Any]:
    """
    Compute aggregate statistics from per-test-case results.
    Returns a dict with overall pass rate and per-assertion rates.
    """
    n = len(all_results)
    if n == 0:
        return {}

    # Per-assertion pass counts
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
    """
    Identify top failure patterns to guide optimization.
    Returns structured failure analysis.
    """
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

    # Sort assertions by failure frequency
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
    """Print a human-readable summary to stdout."""
    sep = '-' * 60
    print(f"\n{sep}")
    print(f"RAPID SOURCE SKILL EVAL RESULTS")
    print(f"Skill file : {skill_path}")
    print(f"Model      : {MODEL}")
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
        bar = '█' * bar_fill + '░' * (20 - bar_fill)
        flag = ' ⚠' if rate < 0.70 else ''
        print(f"  {name:<25} {bar} {rate:.0%} ({count}/{n_total}){flag}")

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
        print(f"  {'ID':<12} {'ALL':<5} {' '.join(n[:8] for n in ASSERTION_NAMES)}")
        for result in verbose_results:
            tc_id = result.get('id', 'unknown')
            scores = result.get('assertion_scores', {})
            passed_all = all(scores.get(n, False) for n in ASSERTION_NAMES)
            all_str = 'PASS' if passed_all else 'FAIL'
            score_str = ' '.join('T' if scores.get(n, False) else 'F' for n in ASSERTION_NAMES)
            print(f"  {tc_id:<12} {all_str:<5} {score_str}")

    print(f"\n{sep}")
    print(f"Results saved to: results/latest_run.json")
    print(sep)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Evaluate a rapid-source skill file against 15 test cases.'
    )
    parser.add_argument(
        'skill_file',
        type=Path,
        help='Path to the skill .md file (e.g. prompts/current.md)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print per-test-case assertion results'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without calling the API — useful for testing the harness itself'
    )
    args = parser.parse_args()

    # Resolve paths relative to project root if relative paths given
    skill_path = args.skill_file
    if not skill_path.is_absolute():
        skill_path = PROJECT_ROOT / skill_path

    # Load skill file and test cases
    skill_content = load_skill_file(skill_path)
    test_cases = load_test_cases()

    print(f"Loaded {len(test_cases)} test cases from {TEST_CASES_PATH}")
    print(f"Evaluating: {skill_path.relative_to(PROJECT_ROOT)}")
    print(f"Model: {MODEL}")

    if not args.dry_run:
        client = get_anthropic_client()
    else:
        client = None
        print("DRY RUN MODE: API calls will be skipped; all outputs will be empty strings.")

    # Ensure results directory exists
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
                client,
                system_prompt=skill_content,
                user_message=user_input,
            )
            # Small delay to be a good API citizen
            time.sleep(0.5)

        if output is None:
            print(' ERROR (API call failed)')
            output = ''

        # Score the output
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
            result['output'] = output  # Include full output in verbose mode

        all_results.append(result)

    # Compute summary stats
    summary = compute_summary(all_results)
    failure_analysis = analyze_failures(all_results)

    # Build the full results object
    run_results = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'skill_file': str(skill_path.relative_to(PROJECT_ROOT)),
        'model': MODEL,
        'summary': summary,
        'failure_analysis': failure_analysis,
        'test_results': all_results,
    }

    # Save to results/latest_run.json
    latest_path = RESULTS_DIR / 'latest_run.json'
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(run_results, f, indent=2, default=str)

    # Also save a timestamped copy for history
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    skill_stem = skill_path.stem
    archive_path = RESULTS_DIR / f'run_{ts}_{skill_stem}.json'
    with open(archive_path, 'w', encoding='utf-8') as f:
        json.dump(run_results, f, indent=2, default=str)

    # Print summary
    verbose_data = all_results if args.verbose else None
    print_summary(skill_path, summary, failure_analysis, verbose_data)

    # Exit with non-zero code if pass rate < 90%
    pass_rate = summary.get('overall_pass_rate', 0)
    sys.exit(0 if pass_rate >= 0.90 else 1)


if __name__ == '__main__':
    main()
