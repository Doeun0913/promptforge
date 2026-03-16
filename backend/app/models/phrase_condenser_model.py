"""Phrase-to-word condenser model wrapper."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CondenseResult:
    condensed: str
    replacements: list[tuple[str, str]]


class PhraseCondenserModel:
    def __init__(self) -> None:
        self._model = None

    async def load(self) -> None:
        # TODO: load phrase condenser resources / model
        pass

    async def condense(self, text: str) -> CondenseResult:
        # TODO: dictionary lookup + context-aware BERT verification
        return CondenseResult(condensed=text, replacements=[])
