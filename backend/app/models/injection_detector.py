"""Injection detector model wrapper.

Fine-tuned binary classifier: injection vs. benign.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InjectionResult:
    is_injection: bool
    risk_score: float
    detected_patterns: list[str]


class InjectionDetectorModel:
    def __init__(self) -> None:
        self._model = None

    async def load(self) -> None:
        # TODO: load fine-tuned injection detection model
        pass

    async def detect(self, text: str) -> InjectionResult:
        # TODO: pattern matching + ML classifier
        return InjectionResult(
            is_injection=False, risk_score=0.0, detected_patterns=[]
        )
