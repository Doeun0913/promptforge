"""Stage 14: Language Normalizer.

Detects mixed Korean/English (code-switching) and normalises to the
dominant language while preserving technical terms in English.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import PipelineContext


class LanguageNormalizerStage(BaseStage):
    stage_id = "s14_lang"
    stage_name = "S14: Language Normalizer"
    description = "Normalizes mixed Korean/English code-switching"
    modifies_semantics = False

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: language detection (fasttext / langdetect)
        # TODO: code-switching point detection
        # TODO: selective normalization with tech-term whitelist
        return StageResult(text=ctx.user_prompt, confidence=1.0)
