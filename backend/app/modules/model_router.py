"""Multi-LLM Router – routes prompts to the most cost-effective model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RoutingDecision:
    model: str
    reason: str
    estimated_cost_usd: float = 0.0


class ModelRouter:
    ROUTING_TABLE: dict[str, dict[str, str]] = {
        "casual": {"simple": "gpt-4o-mini", "complex": "gpt-4o"},
        "coding": {"simple": "gpt-4o-mini", "complex": "gpt-4o"},
        "creative": {"simple": "gpt-4o", "complex": "gpt-4o"},
        "academic": {"simple": "gpt-4o", "complex": "gpt-4o"},
        "translation": {"simple": "gpt-4o-mini", "complex": "gpt-4o"},
        "business": {"simple": "gpt-4o-mini", "complex": "gpt-4o"},
    }

    async def route(
        self,
        domain: str,
        complexity: float = 0.5,
        user_override: str | None = None,
    ) -> RoutingDecision:
        if user_override:
            return RoutingDecision(model=user_override, reason="user override")

        bucket = "complex" if complexity > 0.6 else "simple"
        model = self.ROUTING_TABLE.get(domain, {}).get(bucket, "gpt-4o-mini")
        return RoutingDecision(model=model, reason=f"domain={domain}, complexity={bucket}")
