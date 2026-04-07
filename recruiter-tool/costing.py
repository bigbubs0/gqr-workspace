from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PricingConfig:
    input_per_token: float = 2.50 / 1_000_000
    cached_input_per_token: float = 0.25 / 1_000_000
    output_per_token: float = 15.00 / 1_000_000
    long_context_input_threshold: int = 272_000
    long_context_input_multiplier: float = 2.0
    long_context_output_multiplier: float = 1.5
    long_context_cached_input_multiplier: float = 1.0


GPT54_PRICING = PricingConfig()


def estimate_gpt54_costs(
    input_tokens: int,
    cached_input_tokens: int,
    output_tokens: int,
    *,
    pricing: PricingConfig = GPT54_PRICING,
) -> dict:
    input_tokens = max(int(input_tokens or 0), 0)
    cached_input_tokens = max(int(cached_input_tokens or 0), 0)
    output_tokens = max(int(output_tokens or 0), 0)

    fresh_input_tokens = max(input_tokens - cached_input_tokens, 0)
    long_context = input_tokens > pricing.long_context_input_threshold

    input_multiplier = pricing.long_context_input_multiplier if long_context else 1.0
    cached_multiplier = pricing.long_context_cached_input_multiplier if long_context else 1.0
    output_multiplier = pricing.long_context_output_multiplier if long_context else 1.0

    input_cost = fresh_input_tokens * pricing.input_per_token * input_multiplier
    cached_input_cost = cached_input_tokens * pricing.cached_input_per_token * cached_multiplier
    output_cost = output_tokens * pricing.output_per_token * output_multiplier
    total_cost = input_cost + cached_input_cost + output_cost

    return {
        "llm.cost_input_usd": round(input_cost, 8),
        "llm.cost_cached_input_usd": round(cached_input_cost, 8),
        "llm.cost_output_usd": round(output_cost, 8),
        "run.estimated_cost_usd": round(total_cost, 8),
        "llm.long_context_pricing_applied": long_context,
    }
