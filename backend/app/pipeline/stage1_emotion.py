"""Stage 1: Emotion-Aware Layer Separator.

Separates prompts into an emotion layer and an intent layer.
Emotion metadata is preserved; only the intent layer continues
through the rest of the pipeline.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import EmotionLayer, PipelineContext


class EmotionSeparatorStage(BaseStage):
    stage_id = "s1_emotion"
    stage_name = "S1: Emotion Layer Separator"
    description = "Separates emotion vs. intent layers"
    modifies_semantics = True

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: integrate fine-tuned emotion classifier (XLM-RoBERTa)
        # TODO: pattern-matching for emoticons / interjections / Korean endings
        # For now, treat full text as intent layer.
        ctx.emotion_layer = EmotionLayer()
        return StageResult(text=ctx.user_prompt, confidence=1.0)
