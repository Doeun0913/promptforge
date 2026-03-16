"""Stage 0.5: Korean-Specific Preprocessor.

Handles honorific normalization (존댓말→반말), particle optimization,
ending compression, and basic spacing/spelling correction.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import PipelineContext


class KoreanPreprocessStage(BaseStage):
    stage_id = "s0b_korean"
    stage_name = "S0.5: Korean Preprocessor"
    description = "Korean-specific normalization (honorifics, particles, endings)"
    modifies_semantics = False

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: implement honorific→plain normalization
        # TODO: implement particle/ending compression rules
        # TODO: integrate soynlp / py-hanspell for spacing/spelling
        return StageResult(text=ctx.user_prompt, confidence=1.0)
