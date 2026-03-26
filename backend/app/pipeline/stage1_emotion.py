"""Stage 1: Emotion-Aware Layer Separator.

사용자 프롬프트를 감정 레이어와 의도 레이어로 분리한다.
감정 메타데이터는 EmotionLayer에 보존되며, 의도 텍스트(intent_text)만
하위 파이프라인으로 전달된다.

Phase 1.5 (현재):
    - AI 감정 분류 (snunlp/KR-FinBert-SC) + 규칙 기반 폴백
    - 패턴 매칭으로 감정 표현(expressions) 추출
    - intent_text 초기화 (감정 표현 제거는 Phase 2에서 정교화)
    - 멀티턴 감정 이력(emotion_history) 누적

Phase 2 (예정):
    - KcBERT + KLUE-BERT 앙상블으로 sentiment_score 정밀화
    - 감정 표현 정확한 span 추출 후 intent_text에서 제거
    - requires_reanalysis 자동 판정 (이전 턴 감정 변화 비교)
    - frustration_streak 기반 적극 개입 전략 트리거

재분석 흐름:
    requires_reanalysis=True 시 하위 스테이지(rewriter, structurer 등)가
    reanalysis_reason을 프롬프트 방향 수정 맥락으로 자동 삽입한다.
"""

from __future__ import annotations

import re
import logging

from .base import BaseStage, StageResult
from .context import EmotionLayer, EmotionSnapshot, PipelineContext, Sentiment

logger = logging.getLogger(__name__)

# ── 감정 분류기 (싱글턴) ──────────────────────────────────────────────────

_classifier = None


def _get_classifier():
    """EmotionClassifierModel 싱글턴 반환."""
    global _classifier
    if _classifier is None:
        from app.models.emotion_classifier import EmotionClassifierModel
        _classifier = EmotionClassifierModel()
    return _classifier


# ── 감정 표현 추출 헬퍼 ───────────────────────────────────────────────────


def _extract_expressions(text: str) -> list[str]:
    """텍스트에서 감정 표현 조각을 추출한다.

    patterns.py의 get_all_negative_patterns() (정적+동적 병합)와
    Layer 2/3 정규식을 사용한다.

    Returns:
        감정 표현 문자열 목록. 예: ["아씨", "왜 자꾸 틀려", "ㅠㅠ"]
    """
    from app.utils.patterns import (
        NEGATIVE_EMOTION_CLAUSE_PATTERNS,
        NEGATIVE_EMOTION_JAMO_PATTERNS,
        POSITIVE_EMOTION_JAMO_PATTERNS,
        get_all_negative_patterns,
        get_all_positive_patterns,
    )

    found: list[str] = []

    # Layer 1: 문자열 직접 매칭 (부정 + 긍정)
    for pattern in get_all_negative_patterns() + get_all_positive_patterns():
        if pattern in text:
            found.append(pattern)

    # Layer 2: 절 단위 정규식 (부정)
    for regex in NEGATIVE_EMOTION_CLAUSE_PATTERNS:
        m = re.search(regex, text)
        if m:
            found.append(m.group(0))

    # Layer 3: 자모/반복 패턴
    for regex in NEGATIVE_EMOTION_JAMO_PATTERNS + POSITIVE_EMOTION_JAMO_PATTERNS:
        m = re.search(regex, text)
        if m:
            found.append(m.group(0))

    # 중복 제거 (순서 유지)
    seen: set[str] = set()
    unique: list[str] = []
    for expr in found:
        if expr not in seen:
            seen.add(expr)
            unique.append(expr)
    return unique


def _determine_reanalysis(
    current_sentiment: Sentiment,
    emotion_history: list[EmotionSnapshot],
    frustration_streak: int,
) -> tuple[bool, str | None]:
    """재분석 필요 여부와 사유를 판단한다.

    Phase 2 spec 조건:
        1. sentiment == NEGATIVE AND
        2. 이전 턴 sentiment != NEGATIVE (감정 변화)
           OR frustration_streak >= 2 (연속 부정)
    """
    if current_sentiment != Sentiment.NEGATIVE:
        return False, None

    if frustration_streak >= 2:
        return True, f"연속 {frustration_streak}턴 부정 감정 지속 — 접근 방식 전환 필요"

    if emotion_history:
        prev = emotion_history[-1]
        if prev.sentiment != Sentiment.NEGATIVE:
            return True, "이전 답변에 불만족 감지 — 다른 방향으로 재시도 필요"

    # 첫 턴 부정: 재분석 불필요 (일반 불만 표현)
    return False, None


# ── Stage ─────────────────────────────────────────────────────────────────


class EmotionSeparatorStage(BaseStage):
    stage_id = "s1_emotion"
    stage_name = "S1: Emotion Layer Separator"
    description = "Separates emotion vs. intent layers using AI classifier"
    modifies_semantics = True

    async def process(self, ctx: PipelineContext) -> StageResult:
        """감정 분류 + 표현 추출 + EmotionLayer 초기화."""
        text = ctx.user_prompt

        # 1) AI 감정 분류 (+ 규칙 기반 폴백 자동 전환)
        classifier = _get_classifier()
        prediction = await classifier.predict(text)

        if prediction.used_fallback:
            logger.debug("S1: 규칙 기반 폴백 사용 (AI 모델 없음)")

        # 2) 감정 표현 추출
        expressions = _extract_expressions(text)

        # 3) intent_text: Phase 1.5에서는 원문 전체 유지
        #    Phase 2에서 expressions 정확한 span 제거 후 덮어씀
        intent_text = text

        # 4) frustration_streak 갱신
        prev_layer = ctx.emotion_layer
        prev_streak = prev_layer.frustration_streak if prev_layer else 0
        if prediction.sentiment == Sentiment.NEGATIVE:
            frustration_streak = prev_streak + 1
        else:
            frustration_streak = 0

        # 5) 재분석 필요 여부 판단
        requires_reanalysis, reanalysis_reason = _determine_reanalysis(
            prediction.sentiment,
            prev_layer.emotion_history if prev_layer else [],
            frustration_streak,
        )

        if requires_reanalysis:
            logger.info(
                "S1: requires_reanalysis=True — %s (streak=%d)",
                reanalysis_reason,
                frustration_streak,
            )

        # 6) 현재 턴 스냅샷 생성
        snapshot = EmotionSnapshot(
            turn_index=ctx.turn_index,
            emotions=prediction.emotions,
            sentiment=prediction.sentiment,
            sentiment_score=prediction.sentiment_score,
            expressions=expressions,
        )

        # 7) emotion_history 누적 (이전 히스토리 유지)
        history = list(prev_layer.emotion_history) if prev_layer else []
        history.append(snapshot)

        # 8) EmotionLayer 설정
        ctx.emotion_layer = EmotionLayer(
            emotions=prediction.emotions,
            confidence=prediction.confidence,
            expressions=expressions,
            sentiment=prediction.sentiment,
            sentiment_score=prediction.sentiment_score,
            intent_text=intent_text,
            requires_reanalysis=requires_reanalysis,
            reanalysis_reason=reanalysis_reason,
            emotion_history=history,
            frustration_streak=frustration_streak,
        )

        return StageResult(
            text=intent_text,
            confidence=prediction.confidence if prediction.confidence > 0 else 1.0,
            metadata={
                "sentiment": prediction.sentiment.value,
                "sentiment_score": prediction.sentiment_score,
                "expressions_count": len(expressions),
                "requires_reanalysis": requires_reanalysis,
                "used_fallback": prediction.used_fallback,
                "frustration_streak": frustration_streak,
            },
        )
