"""Stage 11: System Prompt Optimizer ★ Novel.

Compresses and deduplicates the system prompt, and removes overlap
between system prompt and user prompt.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import PipelineContext


class SystemPromptOptimizerStage(BaseStage):
    stage_id = "s11_system"
    stage_name = "S11: System Prompt Optimizer"
    description = "Compresses system prompt and removes system↔user overlap"
    modifies_semantics = True

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: apply S6/S7 compression logic to system_prompt
        # TODO: detect contradictions within system prompt
        # TODO: detect system↔user duplicate instructions and remove from user
        return StageResult(text=ctx.user_prompt, confidence=1.0)
