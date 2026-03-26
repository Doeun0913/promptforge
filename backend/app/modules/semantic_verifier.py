"""Semantic Equivalence Verifier — NLI 기반 의미 보존 독립 검증.

ConfidenceGate와 별개로 동작하는 2차 안전망.
Gate ACCEPT 후에도 NLI 함의 검증 실패 시 원본으로 롤백한다.
"""

from __future__ import annotations

import logging

from app.models.nli_verifier import NLIVerification, NLIVerifierModel

logger = logging.getLogger(__name__)


class SemanticVerifier:
    def __init__(
        self,
        model_name: str = "cross-encoder/nli-deberta-v3-base",
        threshold: float = 0.85,
    ) -> None:
        self._nli = NLIVerifierModel(model_name=model_name, threshold=threshold)

    async def load(self) -> None:
        await self._nli.load()
        if self._nli.is_ready:
            logger.info("SemanticVerifier 준비 완료")
        else:
            logger.warning("SemanticVerifier: NLI 모델 없음 — 검증 스킵 모드")

    @property
    def is_ready(self) -> bool:
        return self._nli.is_ready

    async def verify(self, original: str, compressed: str) -> NLIVerification:
        return await self._nli.verify(original, compressed)

    async def should_rollback(self, original: str, compressed: str) -> bool:
        result = await self.verify(original, compressed)
        return not result.is_equivalent
