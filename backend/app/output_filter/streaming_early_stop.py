"""OF0: Streaming Early Stop Engine.

Monitors the LLM response stream and terminates when the semantic
content is complete (e.g. code block ends, digression begins).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class StopRule:
    domain: str
    patterns: list[str]
    description: str = ""


class StreamingEarlyStopEngine:
    def __init__(self) -> None:
        self._rules: list[StopRule] = []

    def register_rule(self, rule: StopRule) -> None:
        self._rules.append(rule)

    async def monitor(
        self,
        stream: AsyncIterator[str],
        domain: str = "unknown",
    ) -> AsyncIterator[str]:
        # TODO: implement real-time semantic completeness detection
        # TODO: domain-specific stop pattern matching
        async for chunk in stream:
            yield chunk
