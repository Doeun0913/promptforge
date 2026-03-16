"""Output Strategy Engine – the brain that auto-decides output optimization.

Receives S0 domain classification + question-type classification and
automatically determines which of the 5 output optimization techniques
to apply and their parameters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OutputStrategy:
    output_format: str = "free"         # free | json | code_block | list | table
    max_tokens: int | None = None
    constraint_instruction: str = ""
    schema: dict[str, Any] | None = None
    streaming_stop_rule: str | None = None
    progressive_response: bool = False
    use_cache: bool = True
    post_filter_strength: str = "balanced"  # aggressive | balanced | off


class OutputStrategyEngine:
    """Fully automatic output optimization decision engine."""

    async def decide(
        self,
        domain: str,
        question_type: str | None = None,
        prompt_complexity: float = 0.5,
        user_history: dict[str, Any] | None = None,
    ) -> OutputStrategy:
        # TODO: domain + question-type → strategy mapping table
        # TODO: incorporate user feedback history
        # TODO: dynamic max_tokens prediction model
        return OutputStrategy()
