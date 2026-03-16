"""Confidence Gate – decides whether a semantic-modifying transformation is safe."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class GateMode(str, Enum):
    AUTO = "auto"
    SEMI = "semi"
    MANUAL = "manual"


class GateDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    ASK_USER = "ask_user"


@dataclass
class GateVerdict:
    decision: GateDecision
    confidence: float
    stage_id: str
    original_text: str
    transformed_text: str
    reason: str = ""


class ConfidenceGate:
    """
    Evaluates transformation confidence and decides:
    - ACCEPT  → use the transformed text
    - REJECT  → keep original text
    - ASK_USER → surface to UI for human confirmation
    """

    def __init__(
        self,
        mode: GateMode = GateMode.AUTO,
        auto_threshold: float = 0.95,
        semi_lower: float = 0.70,
        semi_upper: float = 0.95,
    ) -> None:
        self.mode = mode
        self.auto_threshold = auto_threshold
        self.semi_lower = semi_lower
        self.semi_upper = semi_upper

        self._pending_verdicts: list[GateVerdict] = []

    def evaluate(
        self,
        confidence: float,
        stage_id: str,
        original_text: str,
        transformed_text: str,
    ) -> GateVerdict:
        decision = self._decide(confidence)
        verdict = GateVerdict(
            decision=decision,
            confidence=confidence,
            stage_id=stage_id,
            original_text=original_text,
            transformed_text=transformed_text,
        )

        if decision == GateDecision.ASK_USER:
            self._pending_verdicts.append(verdict)

        return verdict

    def _decide(self, confidence: float) -> GateDecision:
        if self.mode == GateMode.MANUAL:
            return GateDecision.ASK_USER

        if self.mode == GateMode.AUTO:
            return (
                GateDecision.ACCEPT
                if confidence >= self.auto_threshold
                else GateDecision.REJECT
            )

        # SEMI mode
        if confidence >= self.semi_upper:
            return GateDecision.ACCEPT
        if confidence >= self.semi_lower:
            return GateDecision.ASK_USER
        return GateDecision.REJECT

    @property
    def pending_verdicts(self) -> list[GateVerdict]:
        return list(self._pending_verdicts)

    def resolve_pending(self, index: int, accept: bool) -> None:
        if 0 <= index < len(self._pending_verdicts):
            v = self._pending_verdicts[index]
            v.decision = GateDecision.ACCEPT if accept else GateDecision.REJECT

    def clear_pending(self) -> None:
        self._pending_verdicts.clear()
