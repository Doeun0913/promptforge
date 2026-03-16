"""Intent-preserving rewriter model wrapper.

Wraps a fine-tuned T5 / mBART for Korean intent-preserving paraphrasing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RewriteResult:
    rewritten: str
    confidence: float


class IntentRewriterModel:
    def __init__(self, model_name: str = "t5-base") -> None:
        self.model_name = model_name
        self._model = None

    async def load(self) -> None:
        # TODO: load fine-tuned T5/mBART checkpoint
        pass

    async def rewrite(self, text: str) -> RewriteResult:
        # TODO: seq2seq inference
        return RewriteResult(rewritten=text, confidence=1.0)
