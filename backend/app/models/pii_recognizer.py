"""PII recognizer model wrapper (NER-based)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PIIEntity:
    text: str
    label: str  # NAME, PHONE, EMAIL, ADDRESS, ID_NUMBER, etc.
    start: int
    end: int


class PIIRecognizerModel:
    def __init__(self) -> None:
        self._model = None

    async def load(self) -> None:
        # TODO: load NER model + compile regex patterns
        pass

    async def recognize(self, text: str) -> list[PIIEntity]:
        # TODO: regex patterns + NER inference
        return []
