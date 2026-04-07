from __future__ import annotations

import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, RateLimitError

from costing import estimate_gpt54_costs
from telemetry import compute_output_token_zscore, span

load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5.4")
REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "medium")
MAX_ATTEMPTS = 3

SYSTEM_PROMPT = (
    "You are a specialized AI assistant for executive recruiting in biotech/pharma. "
    "You extract structured data from interview notes with high accuracy."
)

EXTRACTION_PROMPT = """You are an AI assistant helping a biotech/pharma executive recruiter extract structured information from candidate interview notes or transcripts.

CONTEXT: The recruiter focuses on clinical development roles (VPs, Directors, Medical Directors) in biotech/pharma. Key things that matter:
- Big Pharma to Biotech transitions (highly valued)
- Phase progression experience (especially Phase 2+)
- Power companies: Amgen, Genentech, BMS, Pfizer, Regeneron, Vertex, Gilead
- Therapeutic area depth (oncology, rare disease, immunology, CNS)
- Regulatory experience (FDA meetings, IND filings, breakthrough designations)
- Team building from scratch

RED FLAGS TO DETECT:
- Jobs held for less than 1 year (unless contractor role or known layoff)
- Compliance/regulatory issues mentioned
- Unrealistic compensation expectations (>30% jump without justification)
- Location inflexibility when role requires relocation
- Vague about accomplishments or technical details

Extract the following information from the interview notes/transcript and return ONLY valid JSON:

{
  "name": "Full name",
  "current_company": "Current employer",
  "current_title": "Current job title",
  "years_experience_total": <number or null>,
  "years_experience_therapeutic": <number or null>,
  "technical_skills": ["IND filings", "Phase 2 trials", "Oncology", etc.],
  "compensation_current_min": <number or null>,
  "compensation_current_max": <number or null>,
  "compensation_target_min": <number or null>,
  "compensation_target_max": <number or null>,
  "notice_period": "2 weeks / 1 month / etc.",
  "location": "City, State",
  "open_to_relocation": true/false,
  "red_flags": "Comma-separated list of concerns, or empty string if none",
  "why_interesting": "3-sentence narrative about why this candidate stands out, focusing on clinical development trajectory, power company experience, therapeutic depth, and cultural fit signals",
  "therapeutic_areas": ["oncology", "rare disease", etc.],
  "phase_experience": ["Preclinical", "Phase 1", "Phase 2", "Phase 3", "NDA/BLA"]
}

IMPORTANT INSTRUCTIONS:
- For compensation ranges (e.g., "$180-200K"), capture BOTH min and max values
- Recognize shorthand: "BP" = Big Pharma, common company abbreviations
- Therapeutic areas should be standardized: "oncology", "CNS", "immunology", "rare disease", "cardiovascular", "metabolic", etc.
- Phase experience: Use standard terms: "Preclinical", "Phase 1", "Phase 2", "Phase 3", "NDA/BLA"
- If information is not mentioned, use null for numbers, empty string for text, empty array for lists
- The "why_interesting" narrative should sound natural and highlight the most compelling aspects
- Return ONLY the JSON object, no additional text

Interview notes/transcript:
"""

CANDIDATE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "name",
        "current_company",
        "current_title",
        "years_experience_total",
        "years_experience_therapeutic",
        "technical_skills",
        "compensation_current_min",
        "compensation_current_max",
        "compensation_target_min",
        "compensation_target_max",
        "notice_period",
        "location",
        "open_to_relocation",
        "red_flags",
        "why_interesting",
        "therapeutic_areas",
        "phase_experience",
    ],
    "properties": {
        "name": {"type": "string"},
        "current_company": {"type": "string"},
        "current_title": {"type": "string"},
        "years_experience_total": {"type": ["integer", "null"]},
        "years_experience_therapeutic": {"type": ["integer", "null"]},
        "technical_skills": {"type": "array", "items": {"type": "string"}},
        "compensation_current_min": {"type": ["integer", "null"]},
        "compensation_current_max": {"type": ["integer", "null"]},
        "compensation_target_min": {"type": ["integer", "null"]},
        "compensation_target_max": {"type": ["integer", "null"]},
        "notice_period": {"type": "string"},
        "location": {"type": "string"},
        "open_to_relocation": {"type": "boolean"},
        "red_flags": {"type": "string"},
        "why_interesting": {"type": "string"},
        "therapeutic_areas": {"type": "array", "items": {"type": "string"}},
        "phase_experience": {"type": "array", "items": {"type": "string"}},
    },
}

TEXT_FIELDS = [
    "name",
    "current_company",
    "current_title",
    "notice_period",
    "location",
    "red_flags",
    "why_interesting",
]
ARRAY_FIELDS = ["technical_skills", "therapeutic_areas", "phase_experience"]
NUMERIC_FIELDS = [
    "years_experience_total",
    "years_experience_therapeutic",
    "compensation_current_min",
    "compensation_current_max",
    "compensation_target_min",
    "compensation_target_max",
]


class CandidateValidationError(Exception):
    def __init__(self, errors: list[str], metrics: dict | None = None):
        self.errors = errors
        self.metrics = metrics or {}
        super().__init__("Candidate validation failed: " + "; ".join(errors))


def get_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _get_value(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _extract_output_text(response: Any) -> str:
    direct_text = _get_value(response, "output_text")
    if direct_text:
        return direct_text

    output = _get_value(response, "output", []) or []
    parts: list[str] = []
    for item in output:
        content_items = _get_value(item, "content", []) or []
        for content in content_items:
            if _get_value(content, "type") == "output_text":
                text = _get_value(content, "text", "")
                if text:
                    parts.append(text)
    return "".join(parts).strip()


def _normalize_candidate_data(candidate_data: dict) -> dict:
    normalized = dict(candidate_data)

    for field_name in TEXT_FIELDS:
        value = normalized.get(field_name, "")
        normalized[field_name] = value if isinstance(value, str) else str(value or "")

    for field_name in ARRAY_FIELDS:
        value = normalized.get(field_name, [])
        normalized[field_name] = value if isinstance(value, list) else []

    for field_name in NUMERIC_FIELDS:
        value = normalized.get(field_name)
        if isinstance(value, float) and value.is_integer():
            normalized[field_name] = int(value)

    return normalized


def validate_candidate_data(candidate_data: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    schema_failure_count = 0

    if not isinstance(candidate_data, dict):
        return ["Model output was not a JSON object"], {"quality.schema_failures": 1}

    if not str(candidate_data.get("name", "")).strip():
        errors.append("name must be a non-empty string")

    for field_name in TEXT_FIELDS:
        if not isinstance(candidate_data.get(field_name, ""), str):
            errors.append(f"{field_name} must be a string")

    for field_name in ARRAY_FIELDS:
        if not isinstance(candidate_data.get(field_name, []), list):
            errors.append(f"{field_name} must be an array")

    for field_name in NUMERIC_FIELDS:
        value = candidate_data.get(field_name)
        if value is not None and not isinstance(value, int):
            errors.append(f"{field_name} must be an integer or null")

    if not isinstance(candidate_data.get("open_to_relocation"), bool):
        errors.append("open_to_relocation must be a boolean")

    schema_failure_count = len(errors)
    return errors, {"quality.schema_failures": schema_failure_count}


def fact_check_candidate_data(candidate_data: dict, transcript: str) -> tuple[list[str], dict]:
    transcript_normalized = (transcript or "").casefold()
    warnings: list[str] = []

    name = candidate_data.get("name", "").strip()
    if name and name.casefold() not in transcript_normalized:
        warnings.append("name not found in transcript")

    current_company = candidate_data.get("current_company", "").strip()
    if current_company and current_company.casefold() not in transcript_normalized:
        warnings.append("current_company not found in transcript")

    metrics = {
        "quality.fact_check_failures": len(warnings),
        "quality.unexpected_tool_loops": 0,
    }

    return warnings, metrics


def _build_input_payload(transcript: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
        },
        {
            "role": "user",
            "content": [{"type": "input_text", "text": EXTRACTION_PROMPT + transcript}],
        },
    ]


def call_candidate_extraction(
    client: OpenAI,
    transcript: str,
    *,
    pipeline_run_id: str,
    parent_span_id: str | None = None,
    model: str = MODEL_NAME,
    reasoning_effort: str = REASONING_EFFORT,
) -> tuple[dict, dict]:
    retry_count = 0
    rate_limit_events = 0

    with span(
        "llm.candidate_extraction",
        "llm",
        pipeline_run_id,
        parent_span_id=parent_span_id,
        model=model,
        reasoning_effort=reasoning_effort,
    ) as llm_span:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            started_ns = time.perf_counter_ns()
            try:
                response = client.responses.create(
                    model=model,
                    input=_build_input_payload(transcript),
                    reasoning={"effort": reasoning_effort},
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "candidate_extraction",
                            "schema": CANDIDATE_SCHEMA,
                            "strict": True,
                        }
                    },
                )

                usage = _get_value(response, "usage")
                input_tokens = int(_get_value(usage, "input_tokens", 0) or 0)
                output_tokens = int(_get_value(usage, "output_tokens", 0) or 0)
                total_tokens = int(_get_value(usage, "total_tokens", input_tokens + output_tokens) or (input_tokens + output_tokens))
                input_details = _get_value(usage, "input_tokens_details")
                cached_input_tokens = int(_get_value(input_details, "cached_tokens", 0) or 0)
                llm_call_ms = round((time.perf_counter_ns() - started_ns) / 1_000_000, 3)
                response_text = _extract_output_text(response)
                candidate_data = _normalize_candidate_data(json.loads(response_text))

                llm_metrics = {
                    "llm.call_ms": llm_call_ms,
                    "llm.input_tokens": input_tokens,
                    "llm.cached_input_tokens": cached_input_tokens,
                    "llm.output_tokens": output_tokens,
                    "llm.total_tokens": total_tokens,
                    "llm.retry_count": retry_count,
                    "llm.http_status_code": 200,
                    "llm.rate_limit_events": rate_limit_events,
                }
                llm_metrics.update(
                    estimate_gpt54_costs(
                        input_tokens=input_tokens,
                        cached_input_tokens=cached_input_tokens,
                        output_tokens=output_tokens,
                    )
                )
                output_zscore = compute_output_token_zscore(output_tokens)
                if output_zscore is not None:
                    llm_metrics["quality.output_token_zscore"] = output_zscore

                llm_span.update_metrics(llm_metrics)
                llm_span.set_attr("response_id", _get_value(response, "id"))

                return candidate_data, {
                    "response_id": _get_value(response, "id"),
                    "model": model,
                    "reasoning_effort": reasoning_effort,
                    **llm_metrics,
                }
            except (RateLimitError, APITimeoutError, APIConnectionError, APIStatusError) as exc:
                retry_count = attempt
                http_status_code = getattr(exc, "status_code", None)
                if isinstance(exc, RateLimitError) or http_status_code == 429:
                    rate_limit_events += 1

                with span(
                    "llm.candidate_extraction.retry",
                    "llm",
                    pipeline_run_id,
                    parent_span_id=llm_span.span_id,
                    model=model,
                    reasoning_effort=reasoning_effort,
                    attempt=attempt,
                ) as retry_span:
                    retry_span.set_error(exc, http_status_code=http_status_code)
                    retry_span.update_metrics(
                        {
                            "llm.call_ms": round((time.perf_counter_ns() - started_ns) / 1_000_000, 3),
                            "llm.retry_count": retry_count,
                            "llm.http_status_code": http_status_code,
                            "llm.rate_limit_events": rate_limit_events,
                        }
                    )

                if attempt == MAX_ATTEMPTS:
                    llm_span.set_error(exc, http_status_code=http_status_code)
                    llm_span.update_metrics(
                        {
                            "llm.retry_count": retry_count,
                            "llm.http_status_code": http_status_code,
                            "llm.rate_limit_events": rate_limit_events,
                        }
                    )
                    raise

                time.sleep(min(2 ** attempt, 8))


def extract_candidate_info(
    transcript: str,
    *,
    pipeline_run_id: str,
    parent_span_id: str | None = None,
) -> tuple[dict, dict]:
    client = get_client()
    candidate_data, llm_metrics = call_candidate_extraction(
        client,
        transcript,
        pipeline_run_id=pipeline_run_id,
        parent_span_id=parent_span_id,
    )

    validation_errors, validation_metrics = validate_candidate_data(candidate_data)
    fact_check_warnings, fact_check_metrics = fact_check_candidate_data(candidate_data, transcript)

    metadata = {
        **llm_metrics,
        **validation_metrics,
        **fact_check_metrics,
        "fact_check_warnings": fact_check_warnings,
    }

    if validation_errors:
        raise CandidateValidationError(validation_errors, metadata)

    return candidate_data, metadata


def generate_candidate_brief(candidate_data: dict) -> str:
    """Generate formatted candidate brief for email/CRM"""
    name = candidate_data.get("name", "Unknown")
    title = candidate_data.get("current_title", "Unknown Title")
    company = candidate_data.get("current_company", "Unknown Company")

    brief = f"{name} - {title} at {company}\n\n"

    brief += "KEY QUALIFICATIONS:\n"
    skills = candidate_data.get("technical_skills", [])
    if skills:
        for skill in skills[:8]:
            brief += f"- {skill}\n"

    exp_total = candidate_data.get("years_experience_total")
    exp_therapeutic = candidate_data.get("years_experience_therapeutic")
    if exp_total:
        brief += f"- {exp_total} years total experience"
        if exp_therapeutic:
            brief += f" ({exp_therapeutic} years in relevant therapeutic area)"
        brief += "\n"

    therapeutic_areas = candidate_data.get("therapeutic_areas", [])
    if therapeutic_areas:
        brief += f"- Therapeutic expertise: {', '.join(therapeutic_areas)}\n"

    phase_exp = candidate_data.get("phase_experience", [])
    if phase_exp:
        brief += f"- Phase experience: {', '.join(phase_exp)}\n"

    brief += "\nCOMPENSATION & AVAILABILITY:\n"

    curr_min = candidate_data.get("compensation_current_min")
    curr_max = candidate_data.get("compensation_current_max")
    targ_min = candidate_data.get("compensation_target_min")
    targ_max = candidate_data.get("compensation_target_max")

    if curr_min and curr_max:
        brief += f"- Current: ${curr_min:,}-${curr_max:,}K"
    elif curr_min:
        brief += f"- Current: ${curr_min:,}K"
    else:
        brief += "- Current: Not disclosed"

    if targ_min and targ_max:
        brief += f" | Target: ${targ_min:,}-${targ_max:,}K\n"
    elif targ_min:
        brief += f" | Target: ${targ_min:,}K\n"
    else:
        brief += " | Target: Not disclosed\n"

    notice_period = candidate_data.get("notice_period", "Not specified")
    brief += f"- Available: {notice_period}\n"

    location = candidate_data.get("location", "Not specified")
    relocation = "Y" if candidate_data.get("open_to_relocation") else "N"
    brief += f"- Location: {location} | Open to relocation: {relocation}\n"

    why_interesting = candidate_data.get("why_interesting", "")
    if why_interesting:
        brief += f"\nWHY THIS CANDIDATE IS INTERESTING:\n{why_interesting}\n"

    red_flags = candidate_data.get("red_flags", "")
    if red_flags and red_flags.strip():
        brief += f"\nRED FLAGS / CONCERNS:\n{red_flags}\n"
    else:
        brief += "\nRED FLAGS / CONCERNS:\nNone identified\n"

    return brief
