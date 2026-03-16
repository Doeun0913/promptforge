"""Stage 13: Prompt Injection Detector.

Detects and blocks malicious prompt injection patterns including
direct injection, indirect injection, and role hijacking.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import PipelineContext


class InjectionDetectorStage(BaseStage):
    stage_id = "s13_injection"
    stage_name = "S13: Injection Detector"
    description = "Detects and blocks prompt injection attacks"
    modifies_semantics = False

    async def process(self, ctx: PipelineContext) -> StageResult:
        # TODO: pattern-matching rules (Korean + English injection phrases)
        # TODO: fine-tuned binary classifier (injection vs. benign)
        # TODO: set ctx.injection_detected / ctx.injection_risk_score
        return StageResult(text=ctx.user_prompt, confidence=1.0)
