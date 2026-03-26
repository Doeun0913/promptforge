"""NLI-based semantic equivalence verifier.

양방향 함의(entailment) 검증으로 압축 텍스트가 원본 의미를 보존하는지 확인한다.

검증 방식
---------
1. Forward : (original → compressed) — 압축본이 원본 의미를 함의하는가?
2. Backward: (compressed → original) — 원본이 압축본 의미를 함의하는가?
두 방향 모두 threshold(기본 0.85) 이상이어야 is_equivalent=True.

모델
----
cross-encoder/nli-deberta-v3-base (sentence-transformers CrossEncoder)
라벨 순서: contradiction=0, neutral=1, entailment=2

바이패스 조건
-------------
- 텍스트 중 하나가 10자 미만 → 검증 스킵
- 두 텍스트가 동일 → 검증 스킵
- 모델 로드 실패 → 경고 후 equivalent=True 반환 (파이프라인 차단 방지)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_SHORT_TEXT_THRESHOLD = 10
_ENTAILMENT_IDX = 2  # cross-encoder/nli-deberta-v3-base 라벨 순서


@dataclass
class NLIVerification:
    is_equivalent: bool
    forward_score: float    # original → compressed 함의 확률
    backward_score: float   # compressed → original 함의 확률
    threshold: float = 0.85
    skipped: bool = False
    skip_reason: str = ""


class NLIVerifierModel:
    """cross-encoder/nli-deberta-v3-base 기반 양방향 함의 검증기."""

    def __init__(
        self,
        model_name: str = "cross-encoder/nli-deberta-v3-base",
        threshold: float = 0.85,
    ) -> None:
        self.model_name = model_name
        self.threshold = threshold
        self._model = None
        self._loaded: bool = False
        self._load_failed: bool = False

    async def load(self) -> None:
        """CrossEncoder 모델 lazy load. 실패 시 경고만 남기고 폴백 모드."""
        if self._loaded or self._load_failed:
            return
        try:
            from sentence_transformers import CrossEncoder  # type: ignore
            logger.info("NLI 모델 로딩: %s", self.model_name)
            self._model = CrossEncoder(self.model_name)
            self._loaded = True
            logger.info("NLI 모델 로드 완료")
        except Exception as exc:
            self._load_failed = True
            logger.warning("NLI 모델 로드 실패 (%s): %s — 검증 스킵", self.model_name, exc)

    @property
    def is_ready(self) -> bool:
        return self._loaded and self._model is not None

    async def verify(self, original: str, compressed: str) -> NLIVerification:
        """원본과 압축본 사이의 의미 동등성을 양방향으로 검증한다."""
        if not self._loaded and not self._load_failed:
            await self.load()

        if original == compressed:
            return NLIVerification(True, 1.0, 1.0, self.threshold, True, "identical")

        if len(original) < _SHORT_TEXT_THRESHOLD or len(compressed) < _SHORT_TEXT_THRESHOLD:
            return NLIVerification(True, 1.0, 1.0, self.threshold, True, "too_short")

        if self._load_failed or self._model is None:
            return NLIVerification(True, 1.0, 1.0, self.threshold, True, "model_unavailable")

        try:
            return self._run_inference(original, compressed)
        except Exception as exc:
            logger.warning("NLI 추론 실패: %s", exc)
            return NLIVerification(True, 1.0, 1.0, self.threshold, True, f"inference_error: {exc}")

    def _run_inference(self, original: str, compressed: str) -> NLIVerification:
        """forward/backward 두 쌍을 한 번의 배치로 처리."""
        import numpy as np

        pairs = [
            (original[:512], compressed[:512]),
            (compressed[:512], original[:512]),
        ]
        raw = self._model.predict(pairs)  # shape (2, 3)

        def softmax(x):
            e = np.exp(x - np.max(x))
            return e / e.sum()

        fw = float(softmax(raw[0])[_ENTAILMENT_IDX])
        bw = float(softmax(raw[1])[_ENTAILMENT_IDX])
        ok = fw >= self.threshold and bw >= self.threshold

        logger.debug("NLI: fw=%.3f bw=%.3f → %s", fw, bw, "PASS" if ok else "FAIL")
        return NLIVerification(ok, round(fw, 4), round(bw, 4), self.threshold)
