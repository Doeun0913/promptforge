"""Stage 4: Multi-Turn Context Deduplicator ★ Core differentiator.

Tracks context across turns in a session and removes repeated
self-introductions / background information.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import PipelineContext


class MultiTurnDeduplicatorStage(BaseStage):
    stage_id = "s4_multiturn"
    stage_name = "S4: Multi-Turn Deduplicator"
    description = "Removes repeated context across conversation turns"
    modifies_semantics = True

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: session-based embedding cache (sliding window)
        # TODO: cosine similarity between current sentences and turn cache
        # TODO: dedup with new-info preservation logic
        return StageResult(text=ctx.user_prompt, confidence=1.0)
