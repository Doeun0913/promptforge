"""Stage 1: Emotion-Aware Layer Separator.

Separates prompts into an emotion layer and an intent layer.
Emotion metadata is preserved; only the intent layer continues
through the rest of the pipeline.

Phase 1: 데이터 구조 초기화만 수행 (intent_text = 원문 전체 유지).
Phase 2에서 실제 BERT 앙상블 분류 및 감정 문장 제거 로직을 구현한다.

재분석 흐름:
    requires_reanalysis=True 시 하위 스테이지(rewriter, structurer 등)가
    reanalysis_reason을 프롬프트 방향 수정 맥락으로 자동 삽입한다.
"""

from __future__ import annotations

from .base import BaseStage, StageResult
from .context import EmotionLayer, PipelineContext


class EmotionSeparatorStage(BaseStage):
    stage_id = "s1_emotion"
    stage_name = "S1: Emotion Layer Separator"
    description = "Separates emotion vs. intent layers"
    modifies_semantics = True

    async def process(self, ctx: PipelineContext) -> StageResult:
        # Phase 1: 구조 초기화 — intent_text는 일단 원문 전체로 설정
        # Phase 2 구현 목록:
        #   1) KcBERT + KLUE-BERT 앙상블로 sentiment / sentiment_score 계산
        #   2) 한국어 감정 패턴(이모티콘, 감탄사, 종결어미 "-네요/군요/잖아" 등) 추출
        #   3) expressions 제거 후 intent_text 생성
        #   4) 이전 턴 EmotionSnapshot과 비교해 requires_reanalysis 결정
        #   5) emotion_history에 현재 턴 스냅샷 추가
        #   6) frustration_streak 갱신
        ctx.emotion_layer = EmotionLayer(
            intent_text=ctx.user_prompt,  # Phase 2에서 감정 문장 제거 후 덮어씀
        )
        return StageResult(text=ctx.user_prompt, confidence=1.0)
