"""Tests for the token-cost estimator in costing.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from costing import GPT54_PRICING, PricingConfig, estimate_gpt54_costs


def test_zero_tokens_produces_zero_costs():
    result = estimate_gpt54_costs(input_tokens=0, cached_input_tokens=0, output_tokens=0)
    assert result["llm.cost_input_usd"] == 0
    assert result["llm.cost_cached_input_usd"] == 0
    assert result["llm.cost_output_usd"] == 0
    assert result["run.estimated_cost_usd"] == 0
    assert result["llm.long_context_pricing_applied"] is False


def test_negative_inputs_clamped_to_zero():
    result = estimate_gpt54_costs(input_tokens=-100, cached_input_tokens=-50, output_tokens=-25)
    assert result["llm.cost_input_usd"] == 0
    assert result["llm.cost_cached_input_usd"] == 0
    assert result["llm.cost_output_usd"] == 0
    assert result["run.estimated_cost_usd"] == 0


def test_none_inputs_treated_as_zero():
    result = estimate_gpt54_costs(input_tokens=None, cached_input_tokens=None, output_tokens=None)
    assert result["run.estimated_cost_usd"] == 0


def test_standard_pricing_matches_published_formula():
    result = estimate_gpt54_costs(input_tokens=1000, cached_input_tokens=250, output_tokens=200)
    assert result["llm.cost_input_usd"] == pytest.approx(0.001875, abs=1e-9)
    assert result["llm.cost_cached_input_usd"] == pytest.approx(0.0000625, abs=1e-9)
    assert result["llm.cost_output_usd"] == pytest.approx(0.003, abs=1e-9)
    assert result["run.estimated_cost_usd"] == pytest.approx(0.0049375, abs=1e-9)
    assert result["llm.long_context_pricing_applied"] is False


def test_cached_input_tokens_clamped_to_total_input():
    """When cached_input_tokens >= input_tokens, fresh input cost should be zero."""
    result = estimate_gpt54_costs(input_tokens=500, cached_input_tokens=1000, output_tokens=100)
    assert result["llm.cost_input_usd"] == 0
    assert result["llm.cost_cached_input_usd"] == pytest.approx(1000 * 0.25 / 1_000_000, abs=1e-12)


def test_threshold_boundary_does_not_trigger_long_context():
    """At exactly the threshold (272_000), long-context multipliers must NOT apply."""
    threshold = GPT54_PRICING.long_context_input_threshold
    result = estimate_gpt54_costs(input_tokens=threshold, cached_input_tokens=0, output_tokens=100)
    assert result["llm.long_context_pricing_applied"] is False


def test_one_token_above_threshold_triggers_long_context():
    threshold = GPT54_PRICING.long_context_input_threshold
    result = estimate_gpt54_costs(input_tokens=threshold + 1, cached_input_tokens=0, output_tokens=100)
    assert result["llm.long_context_pricing_applied"] is True


def test_long_context_doubles_input_cost():
    """Long-context input multiplier is 2.0; verify cost scales accordingly."""
    threshold = GPT54_PRICING.long_context_input_threshold
    short = estimate_gpt54_costs(input_tokens=10_000, cached_input_tokens=0, output_tokens=0)
    long = estimate_gpt54_costs(input_tokens=threshold + 10_000, cached_input_tokens=threshold, output_tokens=0)
    # Long-context fresh-input portion (10k tokens) costs 2x the short-context fresh-input.
    assert long["llm.cost_input_usd"] == pytest.approx(short["llm.cost_input_usd"] * 2, rel=1e-6)


def test_long_context_increases_output_cost_by_1_5x():
    threshold = GPT54_PRICING.long_context_input_threshold
    short = estimate_gpt54_costs(input_tokens=1000, cached_input_tokens=0, output_tokens=1000)
    long = estimate_gpt54_costs(input_tokens=threshold + 1, cached_input_tokens=0, output_tokens=1000)
    assert long["llm.cost_output_usd"] == pytest.approx(short["llm.cost_output_usd"] * 1.5, rel=1e-6)


def test_float_input_coerced_to_int():
    """estimate_gpt54_costs casts to int; ensure floats don't crash and produce sensible results."""
    result = estimate_gpt54_costs(input_tokens=1000.7, cached_input_tokens=250.9, output_tokens=200.1)
    # Both should match the integer-truncated equivalent.
    expected = estimate_gpt54_costs(input_tokens=1000, cached_input_tokens=250, output_tokens=200)
    assert result["run.estimated_cost_usd"] == expected["run.estimated_cost_usd"]


def test_custom_pricing_config_overrides_defaults():
    custom = PricingConfig(
        input_per_token=1.0,
        cached_input_per_token=0.5,
        output_per_token=2.0,
        long_context_input_threshold=100,
        long_context_input_multiplier=10.0,
        long_context_output_multiplier=10.0,
        long_context_cached_input_multiplier=10.0,
    )
    result = estimate_gpt54_costs(
        input_tokens=50, cached_input_tokens=10, output_tokens=5, pricing=custom
    )
    # 40 fresh @ $1, 10 cached @ $0.5, 5 output @ $2 = 40 + 5 + 10 = 55
    assert result["llm.cost_input_usd"] == pytest.approx(40)
    assert result["llm.cost_cached_input_usd"] == pytest.approx(5)
    assert result["llm.cost_output_usd"] == pytest.approx(10)
    assert result["run.estimated_cost_usd"] == pytest.approx(55)


def test_total_equals_sum_of_components():
    """Invariant: total cost must always equal sum of three component costs."""
    cases = [
        (100, 50, 25),
        (1_000_000, 200_000, 50_000),
        (300_000, 100_000, 80_000),  # long context
        (0, 0, 0),
    ]
    for in_tok, cached, out_tok in cases:
        result = estimate_gpt54_costs(input_tokens=in_tok, cached_input_tokens=cached, output_tokens=out_tok)
        component_sum = (
            result["llm.cost_input_usd"]
            + result["llm.cost_cached_input_usd"]
            + result["llm.cost_output_usd"]
        )
        assert result["run.estimated_cost_usd"] == pytest.approx(component_sum, abs=1e-7)


def test_output_keys_are_stable():
    """Telemetry consumers depend on these exact key names."""
    result = estimate_gpt54_costs(input_tokens=1, cached_input_tokens=0, output_tokens=1)
    expected_keys = {
        "llm.cost_input_usd",
        "llm.cost_cached_input_usd",
        "llm.cost_output_usd",
        "run.estimated_cost_usd",
        "llm.long_context_pricing_applied",
    }
    assert set(result.keys()) == expected_keys
