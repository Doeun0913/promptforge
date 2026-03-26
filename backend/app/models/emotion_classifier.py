"""Korean emotion classifier — AI 기반 감정/극성 분류.

AI 감지의 핵심 장점
--------------------
정적 패턴 목록 없이도 신조어·유행어를 자동 처리한다:

    - **서브워드 토크나이징**: "샤갈", "현타", "킹받아" 등은 알려진
      형태소 조각으로 분해되어 문맥 추론에 활용된다.
    - **문맥 어텐션**: 중립 단어도 부정적 문맥이면 NEGATIVE로 분류.
    - **한국어 인터넷 학습**: KcBERT는 SNS·커뮤니티 텍스트로 학습됨.

모델 구성
---------
Phase 1.5 (현재):
    ``snunlp/KR-FinBert-SC`` — 한국어 감정 분류 (3-class: 부정/중립/긍정)
    모델 미설치 시 규칙 기반 폴백(patterns.py) 자동 전환.

Phase 2 (예정):
    ``beomi/kcbert-base`` 기반 fine-tune (0.6 가중치)
    + ``klue/bert-base`` 기반 fine-tune (0.4 가중치) 앙상블.
    공식: ``score = 0.6 × KcBERT_score + 0.4 × KLUE_score``

Phase 2 앙상블 공식:
    ``sentiment_score = P(positive) − P(negative)``
    범위: −1.0 (완전 부정) ~ 0.0 (중립) ~ +1.0 (완전 긍정)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.pipeline.context import Sentiment

logger = logging.getLogger(__name__)

# ── 모델 설정 ─────────────────────────────────────────────────────────────

# Phase 1.5 기본 모델: 한국어 3-class 감정 분류
# 대안: "hun3359/klue-bert-base-sentiment" (5-star → 감정 매핑)
_DEFAULT_MODEL = "snunlp/KR-FinBert-SC"

# 감정 극성 임계값 (spec: emotion-layer-spec.mdc 참조)
_NEGATIVE_THRESHOLD = -0.3   # score < -0.3 → NEGATIVE
_POSITIVE_THRESHOLD = 0.3    # score >  0.3 → POSITIVE

# 라벨 → Sentiment 매핑 (모델별 라벨 차이 정규화)
_LABEL_TO_SENTIMENT: dict[str, Sentiment] = {
    # 한국어 라벨
    "부정": Sentiment.NEGATIVE,
    "중립": Sentiment.NEUTRAL,
    "긍정": Sentiment.POSITIVE,
    # 영어 라벨 (소문자)
    "negative": Sentiment.NEGATIVE,
    "neutral": Sentiment.NEUTRAL,
    "positive": Sentiment.POSITIVE,
    # LABEL_N 형식
    "label_0": Sentiment.NEGATIVE,
    "label_1": Sentiment.NEUTRAL,
    "label_2": Sentiment.POSITIVE,
    # 숫자 형식 (binary: 0=neg, 1=pos)
    "0": Sentiment.NEGATIVE,
    "1": Sentiment.POSITIVE,
    # 별점 형식 (hun3359/klue-bert-base-sentiment)
    "0 star": Sentiment.NEGATIVE,
    "1 star": Sentiment.NEGATIVE,
    "2 star": Sentiment.NEUTRAL,
    "3 star": Sentiment.NEUTRAL,
    "4 star": Sentiment.POSITIVE,
}


# ── 데이터 구조 ───────────────────────────────────────────────────────────


@dataclass
class EmotionPrediction:
    """감정 분류 결과."""

    emotions: list[str]
    """감지된 감정 레이블 목록. 예: ["불만", "짜증"]"""

    confidence: float
    """가장 높은 감정 레이블의 신뢰도 (0.0 ~ 1.0)"""

    all_scores: dict[str, float]
    """각 감정 레이블별 확률. 예: {"불만": 0.82, "걱정": 0.45}"""

    sentiment: Sentiment = Sentiment.NEUTRAL
    """감정 극성 (POSITIVE / NEGATIVE / NEUTRAL)"""

    sentiment_score: float = 0.0
    """극성 점수. 공식: P(positive) − P(negative). 범위: −1.0 ~ +1.0"""

    raw_pos_prob: float = 0.0
    """P(positive) — 앙상블 가중 계산 시 필요"""

    raw_neg_prob: float = 0.0
    """P(negative) — 앙상블 가중 계산 시 필요"""

    used_fallback: bool = False
    """True이면 AI 모델 대신 규칙 기반 폴백이 사용됨"""


# ── 규칙 기반 폴백 ────────────────────────────────────────────────────────


def _rule_based_predict(text: str) -> EmotionPrediction:
    """AI 모델 로드 실패 시 규칙 기반 폴백.

    patterns.py의 정적 목록 + 동적 크롤링 패턴을 사용한다.
    """
    from app.utils.patterns import (
        NEGATIVE_EMOTION_CLAUSE_PATTERNS,
        NEGATIVE_EMOTION_JAMO_PATTERNS,
        POSITIVE_EMOTION_JAMO_PATTERNS,
        get_all_negative_patterns,
        get_all_positive_patterns,
    )
    import re

    neg_hits = 0
    pos_hits = 0

    neg_patterns = get_all_negative_patterns()
    pos_patterns = get_all_positive_patterns()

    for p in neg_patterns:
        if p in text:
            neg_hits += 1

    for p in pos_patterns:
        if p in text:
            pos_hits += 1

    for pattern in NEGATIVE_EMOTION_CLAUSE_PATTERNS + NEGATIVE_EMOTION_JAMO_PATTERNS:
        if re.search(pattern, text):
            neg_hits += 1

    for pattern in POSITIVE_EMOTION_JAMO_PATTERNS:
        if re.search(pattern, text):
            pos_hits += 1

    raw_neg = min(neg_hits * 0.25, 0.9) if neg_hits else 0.0
    raw_pos = min(pos_hits * 0.25, 0.9) if pos_hits else 0.0

    score = raw_pos - raw_neg

    if score < _NEGATIVE_THRESHOLD:
        sentiment = Sentiment.NEGATIVE
    elif score > _POSITIVE_THRESHOLD:
        sentiment = Sentiment.POSITIVE
    else:
        sentiment = Sentiment.NEUTRAL

    return EmotionPrediction(
        emotions=["부정"] if sentiment == Sentiment.NEGATIVE else (
            ["긍정"] if sentiment == Sentiment.POSITIVE else []
        ),
        confidence=max(raw_neg, raw_pos),
        all_scores={"부정": raw_neg, "긍정": raw_pos},
        sentiment=sentiment,
        sentiment_score=score,
        raw_pos_prob=raw_pos,
        raw_neg_prob=raw_neg,
        used_fallback=True,
    )


# ── AI 분류기 ─────────────────────────────────────────────────────────────


class EmotionClassifierModel:
    """한국어 감정 분류 모델 (transformers 기반).

    사용 예::

        classifier = EmotionClassifierModel()
        await classifier.load()
        result = await classifier.predict("아 씨 왜 자꾸 틀려 ㅠㅠ")
        # result.sentiment == Sentiment.NEGATIVE
        # result.sentiment_score ≈ -0.8
        # result.used_fallback == False  (AI 모델 사용 시)

    모델이 설치되지 않았거나 로드 실패 시 규칙 기반 폴백으로 자동 전환된다.
    """

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        self.model_name = model_name
        self._pipeline = None
        self._loaded: bool = False
        self._load_failed: bool = False

    # ── 라이프사이클 ─────────────────────────────────────────────────────

    async def load(self) -> None:
        """모델 로드 (lazy — 첫 predict() 호출 시 자동 호출됨).

        transformers 미설치 또는 모델 다운로드 실패 시 경고만 남기고
        규칙 기반 폴백 모드로 전환한다.
        """
        if self._loaded or self._load_failed:
            return
        try:
            # transformers import는 무거우므로 런타임에 수행
            from transformers import pipeline as hf_pipeline  # type: ignore

            logger.info("감정 분류 모델 로딩: %s", self.model_name)
            self._pipeline = hf_pipeline(
                "text-classification",
                model=self.model_name,
                return_all_scores=True,
                # GPU 있으면 device=0, 없으면 CPU
                device=-1,
            )
            self._loaded = True
            logger.info("감정 분류 모델 로드 완료: %s", self.model_name)

        except Exception as exc:
            self._load_failed = True
            logger.warning(
                "감정 분류 모델 로드 실패 (%s): %s — 규칙 기반 폴백 사용",
                self.model_name,
                exc,
            )

    # ── 추론 ─────────────────────────────────────────────────────────────

    async def predict(self, text: str) -> EmotionPrediction:
        """텍스트의 감정 극성을 분류한다.

        AI 모델을 사용할 수 없으면 규칙 기반 폴백을 반환한다.

        Args:
            text: 분석할 텍스트 (한국어)

        Returns:
            EmotionPrediction — sentiment, sentiment_score, 등 포함
        """
        if not self._loaded and not self._load_failed:
            await self.load()

        if self._load_failed or self._pipeline is None:
            return _rule_based_predict(text)

        try:
            return self._ai_predict(text)
        except Exception as exc:
            logger.warning("AI 감정 추론 실패: %s — 폴백 사용", exc)
            return _rule_based_predict(text)

    def _ai_predict(self, text: str) -> EmotionPrediction:
        """transformers pipeline으로 감정 분류 수행."""
        # pipeline은 동기 함수 — 이 메서드는 이미 asyncio executor 내부에서 호출
        raw: list[list[dict]] = self._pipeline(text[:512])  # 최대 512토큰 제한
        # return_all_scores=True → [[{label, score}, ...]]
        scores_list: list[dict] = raw[0] if raw else []

        raw_pos = 0.0
        raw_neg = 0.0
        all_scores: dict[str, float] = {}

        for item in scores_list:
            label_raw: str = item.get("label", "")
            score: float = float(item.get("score", 0.0))
            label_norm = label_raw.lower().strip()
            all_scores[label_raw] = score

            mapped = _LABEL_TO_SENTIMENT.get(label_norm)
            if mapped == Sentiment.NEGATIVE:
                raw_neg = max(raw_neg, score)
            elif mapped == Sentiment.POSITIVE:
                raw_pos = max(raw_pos, score)

        sentiment_score = raw_pos - raw_neg

        if sentiment_score < _NEGATIVE_THRESHOLD:
            sentiment = Sentiment.NEGATIVE
            emotions = ["부정"]
        elif sentiment_score > _POSITIVE_THRESHOLD:
            sentiment = Sentiment.POSITIVE
            emotions = ["긍정"]
        else:
            sentiment = Sentiment.NEUTRAL
            emotions = []

        confidence = max(raw_pos, raw_neg) if (raw_pos or raw_neg) else 0.0

        return EmotionPrediction(
            emotions=emotions,
            confidence=confidence,
            all_scores=all_scores,
            sentiment=sentiment,
            sentiment_score=round(sentiment_score, 4),
            raw_pos_prob=round(raw_pos, 4),
            raw_neg_prob=round(raw_neg, 4),
            used_fallback=False,
        )

    # ── Phase 2 앙상블 stub ──────────────────────────────────────────────

    async def predict_ensemble(self, text: str) -> EmotionPrediction:
        """Phase 2: KcBERT(0.6) + KLUE-BERT(0.4) 앙상블 추론.

        현재는 단일 모델 predict()를 위임한다.
        Phase 2에서 두 모델의 raw_pos_prob / raw_neg_prob를 가중 평균한다.

        공식::
            score = 0.6 × KcBERT_score + 0.4 × KLUE_score
            KcBERT_score  = P(pos)_kc  − P(neg)_kc
            KLUE_score    = P(pos)_klue − P(neg)_klue
        """
        # TODO(Phase 2): 두 모델 로드 후 가중 앙상블 구현
        return await self.predict(text)
