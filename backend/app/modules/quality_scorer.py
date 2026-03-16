"""PromptForge Score – quantifies prompt quality across four dimensions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QualityScore:
    clarity: float = 0.0       # ambiguity ratio (from S2)
    structure: float = 0.0     # how well separated (from S9)
    efficiency: float = 0.0    # semantic density = meaning units / tokens
    safety: float = 0.0        # injection risk (from S13)
    overall: float = 0.0       # weighted average (0–100)


class QualityScorer:
    WEIGHTS = {
        "clarity": 0.30,
        "structure": 0.25,
        "efficiency": 0.25,
        "safety": 0.20,
    }

    def score(
        self,
        clarity: float = 100.0,
        structure: float = 100.0,
        efficiency: float = 100.0,
        safety: float = 100.0,
    ) -> QualityScore:
        overall = (
            self.WEIGHTS["clarity"] * clarity
            + self.WEIGHTS["structure"] * structure
            + self.WEIGHTS["efficiency"] * efficiency
            + self.WEIGHTS["safety"] * safety
        )
        return QualityScore(
            clarity=clarity,
            structure=structure,
            efficiency=efficiency,
            safety=safety,
            overall=round(overall, 1),
        )
