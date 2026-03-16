"""Stage 2: Ambiguity Detector.

Detects subjective / vague expressions (e.g. "예쁘게", "적당히", "잘")
and proposes concretization strategies.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import PipelineContext


class AmbiguityDetectorStage(BaseStage):
    stage_id = "s2_ambiguity"
    stage_name = "S2: Ambiguity Detector"
    description = "Detects vague/subjective expressions and proposes concretization"
    modifies_semantics = False

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: build ambiguity lexicon + BERT embedding variance scoring
        # TODO: generate concretization suggestions
        return StageResult(text=ctx.user_prompt, confidence=1.0)
