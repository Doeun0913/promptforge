"""Stage 12: PII Masker ★ Novel.

Automatically masks personally identifiable information (names, phone
numbers, emails, addresses) before sending to LLM.  Stores the mapping
so it can be restored in the output post-filter.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import PipelineContext


class PIIMaskerStage(BaseStage):
    stage_id = "s12_pii"
    stage_name = "S12: PII Masker"
    description = "Masks personal information before LLM call"
    modifies_semantics = False

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: regex patterns (phone, email, Korean ID number, etc.)
        # TODO: NER model for person names, addresses
        # TODO: build placeholder mapping in ctx.pii_mapping
        return StageResult(text=ctx.user_prompt, confidence=1.0)
