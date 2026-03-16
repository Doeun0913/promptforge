"""Cost Estimator – computes token cost savings from compression."""

from __future__ import annotations

from dataclasses import dataclass

# USD per 1M tokens
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-4": {"input": 30.0, "output": 60.0},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "claude-3-opus": {"input": 15.0, "output": 75.0},
    "claude-3-sonnet": {"input": 3.0, "output": 15.0},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
}


@dataclass
class CostEstimate:
    model: str
    input_tokens_before: int
    input_tokens_after: int
    output_tokens_estimate: int
    cost_before_usd: float
    cost_after_usd: float
    savings_usd: float
    savings_pct: float


class CostEstimator:
    def estimate(
        self,
        model: str,
        input_before: int,
        input_after: int,
        output_estimate: int = 500,
    ) -> CostEstimate:
        pricing = MODEL_PRICING.get(model, {"input": 1.0, "output": 2.0})

        cost_before = (
            input_before * pricing["input"] / 1_000_000
            + output_estimate * pricing["output"] / 1_000_000
        )
        cost_after = (
            input_after * pricing["input"] / 1_000_000
            + output_estimate * pricing["output"] / 1_000_000
        )
        savings = cost_before - cost_after
        savings_pct = savings / cost_before if cost_before > 0 else 0.0

        return CostEstimate(
            model=model,
            input_tokens_before=input_before,
            input_tokens_after=input_after,
            output_tokens_estimate=output_estimate,
            cost_before_usd=cost_before,
            cost_after_usd=cost_after,
            savings_usd=savings,
            savings_pct=savings_pct,
        )
