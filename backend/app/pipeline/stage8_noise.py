"""Stage 8: Noise Filter.

Removes filler words, greetings, hedges, and other expressions that
do not contribute to the LLM's task comprehension.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import PipelineContext


class NoiseFilterStage(BaseStage):
    stage_id = "s8_noise"
    stage_name = "S8: Noise Filter"
    description = "Removes filler words, greetings, and hedges"
    modifies_semantics = False

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: noise token/pattern dictionary
        # TODO: context-dependent necessity check (attention-score based)
        return StageResult(text=ctx.user_prompt, confidence=1.0)
