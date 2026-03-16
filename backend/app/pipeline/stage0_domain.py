"""Stage 0: Domain & Task Classifier.

Classifies the prompt domain (coding / creative / academic / translation /
casual / business) and adjusts downstream stage parameters accordingly.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import Domain, PipelineContext


class DomainClassifierStage(BaseStage):
    stage_id = "s0_domain"
    stage_name = "S0: Domain Classifier"
    description = "Classifies prompt domain and adjusts downstream strategy"
    modifies_semantics = False

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: integrate fine-tuned XLM-RoBERTa domain classifier
        # For now, pass through unchanged and mark domain as UNKNOWN.
        ctx.domain = Domain.UNKNOWN
        ctx.domain_confidence = 0.0
        return StageResult(text=ctx.user_prompt, confidence=1.0)
