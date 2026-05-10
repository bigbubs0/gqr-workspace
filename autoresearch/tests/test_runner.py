"""Tests for autoresearch/evals/runner.py.

The runner is the eval harness — its scoring, aggregation, and failure analysis
must be reliable, because every skill-quality decision flows through them.

We avoid testing the actual Claude CLI subprocess; instead we exercise the
pure functions (load_test_cases, score_output, compute_summary, analyze_failures)
and use monkeypatch where the subprocess boundary appears.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import runner


# ---------------------------------------------------------------------------
# load_test_cases — file parsing
# ---------------------------------------------------------------------------


def test_load_test_cases_reads_jsonl(monkeypatch, tmp_path: Path):
    cases_path = tmp_path / "test_cases.jsonl"
    cases_path.write_text(
        '{"id": "tc_001", "input": "first case", "metadata": {"function": "clinical_ops", "level": "Director"}}\n'
        '{"id": "tc_002", "input": "second", "metadata": {"function": "biometrics", "level": "Senior"}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(runner, "TEST_CASES_PATH", cases_path)

    cases = runner.load_test_cases()
    assert len(cases) == 2
    assert cases[0]["id"] == "tc_001"
    assert cases[1]["metadata"]["function"] == "biometrics"


def test_load_test_cases_skips_blank_lines(monkeypatch, tmp_path: Path):
    cases_path = tmp_path / "test_cases.jsonl"
    cases_path.write_text(
        '{"id": "tc_001", "input": "x", "metadata": {}}\n'
        '\n'
        '   \n'
        '{"id": "tc_002", "input": "y", "metadata": {}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(runner, "TEST_CASES_PATH", cases_path)
    cases = runner.load_test_cases()
    assert [c["id"] for c in cases] == ["tc_001", "tc_002"]


def test_load_test_cases_skips_malformed_lines(monkeypatch, tmp_path: Path, capsys):
    cases_path = tmp_path / "test_cases.jsonl"
    cases_path.write_text(
        '{"id": "tc_001", "input": "x", "metadata": {}}\n'
        'not valid json at all\n'
        '{"id": "tc_002", "input": "y", "metadata": {}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(runner, "TEST_CASES_PATH", cases_path)

    cases = runner.load_test_cases()
    assert [c["id"] for c in cases] == ["tc_001", "tc_002"]
    captured = capsys.readouterr().out
    assert "Skipping malformed test case" in captured


def test_load_test_cases_exits_when_file_missing(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(runner, "TEST_CASES_PATH", tmp_path / "does_not_exist.jsonl")
    with pytest.raises(SystemExit):
        runner.load_test_cases()


def test_load_skill_file_returns_contents(tmp_path: Path):
    skill_path = tmp_path / "skill.md"
    skill_path.write_text("skill contents here", encoding="utf-8")
    assert runner.load_skill_file(skill_path) == "skill contents here"


def test_load_skill_file_exits_when_missing(tmp_path: Path):
    with pytest.raises(SystemExit):
        runner.load_skill_file(tmp_path / "missing.md")


# ---------------------------------------------------------------------------
# score_output
# ---------------------------------------------------------------------------


def test_score_output_returns_dict_with_all_assertion_keys():
    scores = runner.score_output("", {})
    for name in runner.ASSERTION_NAMES:
        assert name in scores


# ---------------------------------------------------------------------------
# compute_summary
# ---------------------------------------------------------------------------


def _result(tc_id: str, scores: dict, metadata: dict | None = None) -> dict:
    return {
        "id": tc_id,
        "metadata": metadata or {},
        "assertion_scores": scores,
        "passed_all": all(scores.values()),
        "output_length": 100,
        "output_word_count": 20,
    }


def _all_pass_scores() -> dict:
    return {name: True for name in runner.ASSERTION_NAMES}


def _all_fail_scores() -> dict:
    return {name: False for name in runner.ASSERTION_NAMES}


def test_compute_summary_returns_empty_for_no_results():
    assert runner.compute_summary([]) == {}


def test_compute_summary_handles_perfect_pass_rate():
    results = [_result(f"tc_{i}", _all_pass_scores()) for i in range(5)]
    summary = runner.compute_summary(results)
    assert summary["total_cases"] == 5
    assert summary["overall_pass_count"] == 5
    assert summary["overall_pass_rate"] == 1.0
    for name in runner.ASSERTION_NAMES:
        assert summary["per_assertion_pass_rates"][name] == 1.0
        assert summary["per_assertion_pass_counts"][name] == 5


def test_compute_summary_handles_all_fail_rate():
    results = [_result(f"tc_{i}", _all_fail_scores()) for i in range(3)]
    summary = runner.compute_summary(results)
    assert summary["overall_pass_count"] == 0
    assert summary["overall_pass_rate"] == 0.0
    for name in runner.ASSERTION_NAMES:
        assert summary["per_assertion_pass_counts"][name] == 0


def test_compute_summary_counts_partial_passes():
    """A case that passes 7 of 8 assertions counts as a failure of overall_pass but contributes to per-assertion rates."""
    scores_a = _all_pass_scores()
    scores_b = _all_pass_scores()
    scores_b["boolean_depth"] = False  # one specific assertion fails
    results = [_result("tc_a", scores_a), _result("tc_b", scores_b)]
    summary = runner.compute_summary(results)

    assert summary["overall_pass_count"] == 1
    assert summary["overall_pass_rate"] == 0.5
    assert summary["per_assertion_pass_counts"]["boolean_depth"] == 1
    assert summary["per_assertion_pass_rates"]["boolean_depth"] == 0.5
    # All other assertions still pass both cases.
    assert summary["per_assertion_pass_counts"]["not_block"] == 2


def test_compute_summary_pass_rates_are_rounded_to_four_places():
    """Pass rates should be quantized so JSON snapshots don't churn from float noise."""
    # 1/3 = 0.33333..., should round to 0.3333
    scores_a = _all_pass_scores()
    scores_b = _all_fail_scores()
    scores_c = _all_fail_scores()
    results = [_result("a", scores_a), _result("b", scores_b), _result("c", scores_c)]
    summary = runner.compute_summary(results)
    assert summary["overall_pass_rate"] == 0.3333


def test_compute_summary_missing_assertion_key_counts_as_fail():
    """If a case is missing a score key, it should be treated as failed for that assertion."""
    partial = {"boolean_depth": True}  # missing the rest
    results = [_result("tc_partial", partial)]
    summary = runner.compute_summary(results)
    assert summary["per_assertion_pass_counts"]["boolean_depth"] == 1
    for name in runner.ASSERTION_NAMES:
        if name != "boolean_depth":
            assert summary["per_assertion_pass_counts"][name] == 0


# ---------------------------------------------------------------------------
# analyze_failures
# ---------------------------------------------------------------------------


def test_analyze_failures_lists_top_failing_assertions_first():
    """Top-failing assertions are returned in descending count order."""
    scores_a = _all_pass_scores()
    scores_a["boolean_depth"] = False
    scores_a["not_block"] = False
    scores_b = _all_pass_scores()
    scores_b["boolean_depth"] = False
    results = [
        _result("a", scores_a, {"function": "clinical_ops", "level": "Director"}),
        _result("b", scores_b, {"function": "biometrics", "level": "Senior"}),
    ]
    analysis = runner.analyze_failures(results)

    top = dict(analysis["top_failing_assertions"])
    assert top["boolean_depth"] == 2  # fails on both
    assert top["not_block"] == 1
    # Ordering: top entry must be the highest count.
    first_name, first_count = analysis["top_failing_assertions"][0]
    assert first_count == max(top.values())


def test_analyze_failures_groups_by_function_and_level():
    scores = _all_pass_scores()
    scores["client_anonymized"] = False
    results = [
        _result("a", scores, {"function": "clinical_ops", "level": "Director"}),
        _result("b", scores, {"function": "biometrics", "level": "Senior"}),
    ]
    analysis = runner.analyze_failures(results)
    assert "clinical_ops" in analysis["failures_by_function"]
    assert "client_anonymized" in analysis["failures_by_function"]["clinical_ops"]
    assert "biometrics" in analysis["failures_by_function"]
    assert "Director" in analysis["failures_by_level"]
    assert "Senior" in analysis["failures_by_level"]


def test_analyze_failures_handles_missing_metadata_keys():
    """When function or level missing from metadata, fall back to 'unknown'."""
    scores = _all_pass_scores()
    scores["word_count"] = False
    results = [_result("tc_a", scores, {})]
    analysis = runner.analyze_failures(results)
    assert "unknown" in analysis["failures_by_function"]
    assert "unknown" in analysis["failures_by_level"]


def test_analyze_failures_excludes_assertions_with_zero_failures():
    """failures_by_assertion only contains assertions with at least one failing case."""
    scores = _all_pass_scores()
    scores["impact_endings"] = False
    results = [_result("tc_a", scores)]
    analysis = runner.analyze_failures(results)
    assert "impact_endings" in analysis["failures_by_assertion"]
    # Every other assertion had zero failures, so they're filtered out.
    for name in runner.ASSERTION_NAMES:
        if name != "impact_endings":
            assert name not in analysis["failures_by_assertion"]
