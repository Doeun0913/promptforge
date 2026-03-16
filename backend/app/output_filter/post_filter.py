"""Output Post-Filter orchestrator.

Runs OF1→OF2→OF3 on the LLM's raw response before delivering it to the user.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .preamble_remover import PreambleRemover
from .response_dedup import ResponseDeduplicator
from .response_condenser import ResponseCondenser


@dataclass
class OutputFilterResult:
    text: str
    original_tokens: int = 0
    filtered_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class OutputPostFilter:
    """Sequentially applies output post-processing filters."""

    def __init__(self) -> None:
        self.preamble_remover = PreambleRemover()
        self.deduplicator = ResponseDeduplicator()
        self.condenser = ResponseCondenser()

    async def run(self, response_text: str, domain: str = "unknown") -> OutputFilterResult:
        text = response_text

        text = await self.preamble_remover.process(text)
        text = await self.deduplicator.process(text)
        text = await self.condenser.process(text, domain=domain)

        return OutputFilterResult(
            text=text,
            metadata={"domain": domain},
        )
