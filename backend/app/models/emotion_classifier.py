"""Emotion classifier model wrapper.

Phase 1: 데이터 구조만 정의. 실제 모델 로딩/추론은 Phase 2에서 구현.

감정 극성(sentiment_score) 계산 공식:
    sentiment_score = P(positive) - P(negative)
    범위: -1.0 (완전 부정) ~ +1.0 (완전 긍정)

앙상블 전략 (Phase 2):
    score = 0.6 × KcBERT_score + 0.4 × KLUE_score
    - KcBERT : 한국 SNS/구어체·비속어에 강함
    - KLUE-BERT : 표준 한국어·격식체에 강함
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.pipeline.context import Sentiment


@dataclass
class EmotionPrediction:
    emotions: list[str]
    """감지된 감정 레이블 목록. 예: ["불만", "짜증"]"""

    confidence: float
    """가장 높은 감정 레이블의 신뢰도 (0.0 ~ 1.0)"""

    all_scores: dict[str, float]
    """각 감정 레이블별 확률. 예: {"불만": 0.82, "걱정": 0.45}"""

    sentiment: Sentiment = Sentiment.NEUTRAL
    """감정 극성 (POSITIVE / NEGATIVE / NEUTRAL)"""

    sentiment_score: float = 0.0
    """극성 점수. 공식: P(positive) - P(negative). 범위: -1.0 ~ +1.0"""

    raw_pos_prob: float = 0.0
    """softmax 의 P(positive) — 앙상블 가중 계산 시 필요"""

    raw_neg_prob: float = 0.0
    """softmax 의 P(negative) — 앙상블 가중 계산 시 필요"""


class EmotionClassifierModel:
    def __init__(self, model_name: str = "xlm-roberta-base") -> None:
        self.model_name = model_name
        self._model = None

    async def load(self) -> None:
        # TODO(Phase 2): KcBERT + KLUE-BERT 앙상블 로딩
        # 예: self._model = pipeline("text-classification", model="beomi/kcbert-base")
        pass

    async def predict(self, text: str) -> EmotionPrediction:
        # TODO(Phase 2): 실제 추론 구현
        # 1) KcBERT inference  → raw_pos_prob, raw_neg_prob
        # 2) KLUE-BERT inference → raw_pos_prob, raw_neg_prob
        # 3) ensemble_score = 0.6 * kc_score + 0.4 * klue_score
        # 4) sentiment = NEGATIVE if score < -0.3 else POSITIVE if score > 0.3 else NEUTRAL
        return EmotionPrediction(
            emotions=[],
            confidence=0.0,
            all_scores={},
            sentiment=Sentiment.NEUTRAL,
            sentiment_score=0.0,
        )
