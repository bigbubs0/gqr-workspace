"""Tests for ai_processor.py — extraction, validation, fact-checking, brief rendering.

Focus areas (the existing telemetry test exercises retry + cached tokens once;
this file covers the breadth that the boundary code actually needs):
  - validate_candidate_data: every error branch
  - fact_check_candidate_data: missing name / company / casefold matching
  - _normalize_candidate_data: type coercion paths
  - _extract_output_text: direct text vs. nested output items
  - call_candidate_extraction: success path metrics, max-retry exhaustion
  - generate_candidate_brief: formatting edge cases
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from _fakes import (
    FakeClient,
    FakeResponse,
    TemporaryConnectionError,
    VALID_CANDIDATE_PAYLOAD,
)


# ---------------------------------------------------------------------------
# validate_candidate_data
# ---------------------------------------------------------------------------


def test_validate_accepts_well_formed_payload(app_stack):
    errors, metrics = app_stack.ai_processor.validate_candidate_data(dict(VALID_CANDIDATE_PAYLOAD))
    assert errors == []
    assert metrics["quality.schema_failures"] == 0


def test_validate_rejects_non_dict(app_stack):
    errors, metrics = app_stack.ai_processor.validate_candidate_data("not a dict")
    assert errors == ["Model output was not a JSON object"]
    assert metrics["quality.schema_failures"] == 1


def test_validate_rejects_empty_name(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, name="")
    errors, metrics = app_stack.ai_processor.validate_candidate_data(payload)
    assert "name must be a non-empty string" in errors
    assert metrics["quality.schema_failures"] >= 1


def test_validate_rejects_whitespace_only_name(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, name="   ")
    errors, _ = app_stack.ai_processor.validate_candidate_data(payload)
    assert "name must be a non-empty string" in errors


def test_validate_rejects_non_string_text_field(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, current_company=123)
    errors, _ = app_stack.ai_processor.validate_candidate_data(payload)
    assert "current_company must be a string" in errors


def test_validate_rejects_non_list_array_field(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, technical_skills="Phase 2")
    errors, _ = app_stack.ai_processor.validate_candidate_data(payload)
    assert "technical_skills must be an array" in errors


def test_validate_rejects_string_numeric_field(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, years_experience_total="twelve")
    errors, _ = app_stack.ai_processor.validate_candidate_data(payload)
    assert "years_experience_total must be an integer or null" in errors


def test_validate_accepts_null_numeric_fields(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, years_experience_total=None, compensation_target_min=None)
    errors, _ = app_stack.ai_processor.validate_candidate_data(payload)
    assert errors == []


def test_validate_rejects_non_boolean_relocation(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, open_to_relocation="yes")
    errors, _ = app_stack.ai_processor.validate_candidate_data(payload)
    assert "open_to_relocation must be a boolean" in errors


def test_validate_accumulates_multiple_errors(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, name="", technical_skills="not a list", open_to_relocation="no")
    errors, metrics = app_stack.ai_processor.validate_candidate_data(payload)
    assert len(errors) >= 3
    assert metrics["quality.schema_failures"] == len(errors)


# ---------------------------------------------------------------------------
# fact_check_candidate_data
# ---------------------------------------------------------------------------


def test_fact_check_passes_when_name_and_company_present_in_transcript(app_stack):
    transcript = "Jane Doe currently works at Acme Bio and leads programs."
    warnings, metrics = app_stack.ai_processor.fact_check_candidate_data(
        dict(VALID_CANDIDATE_PAYLOAD), transcript
    )
    assert warnings == []
    assert metrics["quality.fact_check_failures"] == 0
    assert metrics["quality.unexpected_tool_loops"] == 0


def test_fact_check_flags_name_not_in_transcript(app_stack):
    transcript = "Some other candidate at Acme Bio."
    warnings, metrics = app_stack.ai_processor.fact_check_candidate_data(
        dict(VALID_CANDIDATE_PAYLOAD), transcript
    )
    assert "name not found in transcript" in warnings
    assert metrics["quality.fact_check_failures"] == 1


def test_fact_check_flags_company_not_in_transcript(app_stack):
    transcript = "Jane Doe leads programs somewhere."
    warnings, _ = app_stack.ai_processor.fact_check_candidate_data(
        dict(VALID_CANDIDATE_PAYLOAD), transcript
    )
    assert "current_company not found in transcript" in warnings


def test_fact_check_is_case_insensitive(app_stack):
    """Name and company should match regardless of casing in the transcript."""
    transcript = "JANE DOE works at acme bio."
    warnings, _ = app_stack.ai_processor.fact_check_candidate_data(
        dict(VALID_CANDIDATE_PAYLOAD), transcript
    )
    assert warnings == []


def test_fact_check_handles_empty_transcript(app_stack):
    warnings, metrics = app_stack.ai_processor.fact_check_candidate_data(
        dict(VALID_CANDIDATE_PAYLOAD), ""
    )
    assert "name not found in transcript" in warnings
    assert "current_company not found in transcript" in warnings
    assert metrics["quality.fact_check_failures"] == 2


def test_fact_check_handles_none_transcript(app_stack):
    warnings, _ = app_stack.ai_processor.fact_check_candidate_data(
        dict(VALID_CANDIDATE_PAYLOAD), None
    )
    assert "name not found in transcript" in warnings


def test_fact_check_skips_empty_name_and_company(app_stack):
    """If the model didn't extract name/company, fact-checker has nothing to verify."""
    payload = dict(VALID_CANDIDATE_PAYLOAD, name="", current_company="")
    warnings, _ = app_stack.ai_processor.fact_check_candidate_data(payload, "any transcript")
    assert warnings == []


# ---------------------------------------------------------------------------
# _normalize_candidate_data
# ---------------------------------------------------------------------------


def test_normalize_coerces_text_fields(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, current_title=None, location=123)
    normalized = app_stack.ai_processor._normalize_candidate_data(payload)
    assert normalized["current_title"] == ""
    assert normalized["location"] == "123"


def test_normalize_replaces_non_list_arrays_with_empty(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, technical_skills="not a list", phase_experience=None)
    normalized = app_stack.ai_processor._normalize_candidate_data(payload)
    assert normalized["technical_skills"] == []
    assert normalized["phase_experience"] == []


def test_normalize_converts_integer_floats_to_int(app_stack):
    payload = dict(VALID_CANDIDATE_PAYLOAD, years_experience_total=12.0, compensation_current_min=200.0)
    normalized = app_stack.ai_processor._normalize_candidate_data(payload)
    assert normalized["years_experience_total"] == 12
    assert isinstance(normalized["years_experience_total"], int)
    assert normalized["compensation_current_min"] == 200


def test_normalize_preserves_non_integer_floats(app_stack):
    """If the model emits a non-integer float, leave it alone (validate will flag it)."""
    payload = dict(VALID_CANDIDATE_PAYLOAD, years_experience_total=12.5)
    normalized = app_stack.ai_processor._normalize_candidate_data(payload)
    assert normalized["years_experience_total"] == 12.5


# ---------------------------------------------------------------------------
# _extract_output_text
# ---------------------------------------------------------------------------


def test_extract_output_text_prefers_direct_attribute(app_stack):
    response = SimpleNamespace(output_text="direct text")
    assert app_stack.ai_processor._extract_output_text(response) == "direct text"


def test_extract_output_text_falls_back_to_nested_output(app_stack):
    response = {
        "output": [
            {"content": [
                {"type": "output_text", "text": "Hello "},
                {"type": "reasoning", "text": "should-be-ignored"},
                {"type": "output_text", "text": "world"},
            ]},
        ]
    }
    assert app_stack.ai_processor._extract_output_text(response) == "Hello world"


def test_extract_output_text_returns_empty_when_no_text(app_stack):
    assert app_stack.ai_processor._extract_output_text({}) == ""
    assert app_stack.ai_processor._extract_output_text(None) == ""


# ---------------------------------------------------------------------------
# call_candidate_extraction — success path metrics
# ---------------------------------------------------------------------------


def test_call_candidate_extraction_records_cost_and_tokens(app_stack):
    client = FakeClient([FakeResponse(dict(VALID_CANDIDATE_PAYLOAD), input_tokens=2000, output_tokens=500, cached_tokens=300)])
    data, metrics = app_stack.ai_processor.call_candidate_extraction(
        client, "Jane Doe at Acme Bio.", pipeline_run_id="run_metrics_case"
    )
    assert data["name"] == "Jane Doe"
    assert metrics["llm.input_tokens"] == 2000
    assert metrics["llm.output_tokens"] == 500
    assert metrics["llm.cached_input_tokens"] == 300
    assert metrics["llm.retry_count"] == 0
    assert metrics["llm.rate_limit_events"] == 0
    assert "run.estimated_cost_usd" in metrics
    assert metrics["llm.http_status_code"] == 200


def test_call_candidate_extraction_counts_rate_limit_events(app_stack, monkeypatch):
    """A RateLimitError-like exception with status_code 429 should bump the rate_limit_events counter."""
    monkeypatch.setattr(app_stack.ai_processor, "APIStatusError", TemporaryConnectionError)
    rate_limited = TemporaryConnectionError("429 rate limit", status_code=429)
    client = FakeClient([rate_limited, FakeResponse(dict(VALID_CANDIDATE_PAYLOAD))])
    _, metrics = app_stack.ai_processor.call_candidate_extraction(
        client, "Jane Doe at Acme Bio.", pipeline_run_id="run_rate_limit_case"
    )
    assert metrics["llm.rate_limit_events"] == 1
    assert metrics["llm.retry_count"] == 1


def test_call_candidate_extraction_raises_after_max_attempts(app_stack, monkeypatch):
    monkeypatch.setattr(app_stack.ai_processor, "time", _NoSleepTime())
    failures = [TemporaryConnectionError(f"fail-{i}") for i in range(app_stack.ai_processor.MAX_ATTEMPTS)]
    client = FakeClient(failures)
    with pytest.raises(TemporaryConnectionError):
        app_stack.ai_processor.call_candidate_extraction(
            client, "Jane Doe at Acme Bio.", pipeline_run_id="run_exhaust_case"
        )


class _NoSleepTime:
    """Stub for the time module so retry backoff doesn't slow tests down."""

    def sleep(self, _seconds):
        return None

    def perf_counter_ns(self):
        import time
        return time.perf_counter_ns()


# ---------------------------------------------------------------------------
# extract_candidate_info — orchestration
# ---------------------------------------------------------------------------


def test_extract_candidate_info_raises_on_validation_error(app_stack, monkeypatch):
    invalid_payload = dict(VALID_CANDIDATE_PAYLOAD, name="")
    client = FakeClient([FakeResponse(invalid_payload)])
    monkeypatch.setattr(app_stack.ai_processor, "get_client", lambda: client)

    with pytest.raises(app_stack.ai_processor.CandidateValidationError) as exc_info:
        app_stack.ai_processor.extract_candidate_info(
            "Acme Bio oncology background.", pipeline_run_id="run_invalid"
        )
    assert "name must be a non-empty string" in exc_info.value.errors


def test_extract_candidate_info_returns_metadata_with_fact_check_warnings(app_stack, monkeypatch):
    client = FakeClient([FakeResponse(dict(VALID_CANDIDATE_PAYLOAD))])
    monkeypatch.setattr(app_stack.ai_processor, "get_client", lambda: client)

    data, metadata = app_stack.ai_processor.extract_candidate_info(
        "Unrelated transcript text.", pipeline_run_id="run_fact_warn"
    )
    assert data["name"] == "Jane Doe"
    # Both name and company missing from transcript => 2 warnings.
    assert metadata["fact_check_warnings"] == [
        "name not found in transcript",
        "current_company not found in transcript",
    ]


# ---------------------------------------------------------------------------
# generate_candidate_brief
# ---------------------------------------------------------------------------


def test_brief_contains_name_title_and_company(app_stack):
    brief = app_stack.ai_processor.generate_candidate_brief(dict(VALID_CANDIDATE_PAYLOAD))
    assert "Jane Doe" in brief
    assert "Director" in brief
    assert "Acme Bio" in brief


def test_brief_formats_compensation_range(app_stack):
    brief = app_stack.ai_processor.generate_candidate_brief(dict(VALID_CANDIDATE_PAYLOAD))
    assert "$200-$220K" in brief
    assert "$240-$260K" in brief


def test_brief_handles_missing_compensation(app_stack):
    candidate = dict(VALID_CANDIDATE_PAYLOAD)
    for key in ("compensation_current_min", "compensation_current_max", "compensation_target_min", "compensation_target_max"):
        candidate[key] = None
    brief = app_stack.ai_processor.generate_candidate_brief(candidate)
    assert "Not disclosed" in brief


def test_brief_indicates_no_red_flags_when_empty(app_stack):
    brief = app_stack.ai_processor.generate_candidate_brief(dict(VALID_CANDIDATE_PAYLOAD, red_flags=""))
    assert "None identified" in brief


def test_brief_shows_red_flags_when_present(app_stack):
    brief = app_stack.ai_processor.generate_candidate_brief(
        dict(VALID_CANDIDATE_PAYLOAD, red_flags="short tenure at last role")
    )
    assert "short tenure at last role" in brief
    assert "None identified" not in brief


def test_brief_renders_relocation_y_or_n(app_stack):
    yes_brief = app_stack.ai_processor.generate_candidate_brief(
        dict(VALID_CANDIDATE_PAYLOAD, open_to_relocation=True)
    )
    no_brief = app_stack.ai_processor.generate_candidate_brief(
        dict(VALID_CANDIDATE_PAYLOAD, open_to_relocation=False)
    )
    assert "Open to relocation: Y" in yes_brief
    assert "Open to relocation: N" in no_brief


def test_brief_limits_skills_to_first_eight(app_stack):
    candidate = dict(VALID_CANDIDATE_PAYLOAD, technical_skills=[f"skill_{i}" for i in range(20)])
    brief = app_stack.ai_processor.generate_candidate_brief(candidate)
    assert "skill_0" in brief
    assert "skill_7" in brief
    assert "skill_8" not in brief


def test_brief_gracefully_handles_unknown_candidate(app_stack):
    """All key fields missing should still produce a valid brief without exceptions."""
    brief = app_stack.ai_processor.generate_candidate_brief({})
    assert "Unknown" in brief
