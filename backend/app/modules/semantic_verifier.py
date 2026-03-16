"""Semantic Equivalence Verifier – independent safety check.

Separate from the Confidence Gate: uses NLI bidirectional entailment
to verify that compressed text genuinely preserves the original meaning.
"""

from __future__ import annotations

from ..models.nli_verifier import NLIVerifierModel, NLIVerification


class SemanticVerifier:
    def __init__(self) -> None:
        self.nli_model = NLIVerifierModel()

    async def load(self) -> None:
        await self.nli_model.load()

    async def verify(self, original: str, compressed: str) -> NLIVerification:
        return await self.nli_model.verify(original, compressed)

    async def should_rollback(self, original: str, compressed: str) -> bool:
        result = await self.verify(original, compressed)
        return not result.is_equivalent
