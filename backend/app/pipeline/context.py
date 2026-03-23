"""Pipeline context: the data object that flows through every stage."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Domain(str, Enum):
    CODING = "coding"
    CREATIVE = "creative"
    ACADEMIC = "academic"
    TRANSLATION = "translation"
    CASUAL = "casual"
    BUSINESS = "business"
    UNKNOWN = "unknown"


class CompressionLevel(str, Enum):
    MINIMAL = "minimal"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class Sentiment(str, Enum):
    """감정 극성(polarity).

    - POSITIVE : 만족·칭찬·감사 등 긍정 표현
    - NEGATIVE : 불만·분노·실망 등 부정 표현 → requires_reanalysis 트리거 후보
    - NEUTRAL  : 감정 신호가 없거나 중립
    """

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class EmotionSnapshot:
    """단일 턴의 감정 상태 스냅샷.

    emotion_history 리스트에 턴마다 쌓여, 멀티턴 감정 흐름을 추적한다.
    """

    turn_index: int
    emotions: list[str]
    sentiment: Sentiment
    sentiment_score: float          # -1.0(매우 부정) ~ +1.0(매우 긍정)
    expressions: list[str] = field(default_factory=list)


@dataclass
class EmotionLayer:
    # ── 기존 필드 ──────────────────────────────────────────────────────────
    emotions: list[str] = field(default_factory=list)
    """감정 레이블 목록. 예: ["불만", "걱정"]"""

    confidence: float = 0.0
    """감정 분류 모델의 전체 신뢰도 (0.0 ~ 1.0)"""

    expressions: list[str] = field(default_factory=list)
    """원문에서 감정을 담고 있는 텍스트 조각. 예: ["아씨", "왜 자꾸 틀려"]"""

    # ── 신규 필드 ──────────────────────────────────────────────────────────
    sentiment: Sentiment = Sentiment.NEUTRAL
    """감정 극성. BERT 앙상블(KcBERT + KLUE-BERT) 출력으로 결정된다."""

    sentiment_score: float = 0.0
    """극성 점수. -1.0(매우 부정) ~ 0.0(중립) ~ +1.0(매우 긍정).
    threshold 예시: score < -0.3 → NEGATIVE 처리."""

    intent_text: str = ""
    """감정 표현을 제거한 순수 의도 텍스트.
    예) "아씨 왜 자꾸 틀리냐고, 파이썬 소수 판별 코드 짜줘"
        → "파이썬 소수 판별 코드 짜줘"
    이 텍스트만 하위 파이프라인(rewriter, structurer 등)에 전달한다."""

    requires_reanalysis: bool = False
    """True이면 이전 답변 방향이 틀렸을 가능성이 있음을 하위 스테이지에 알린다.
    NEGATIVE 감지 + 이전 턴과 감정 변화가 있을 때 Phase 2에서 자동 설정된다."""

    reanalysis_reason: str | None = None
    """재분석 사유. 예: "이전 답변에 불만족", "연속 2턴 부정 감정 지속"
    프롬프트에 방향 수정 맥락으로 자동 삽입할 때 사용한다."""

    emotion_history: list[EmotionSnapshot] = field(default_factory=list)
    """세션 내 이전 턴들의 EmotionSnapshot 누적 목록.
    Phase 2 재분석 로직에서 감정 추세(trend)를 판단하는 데 활용한다."""

    frustration_streak: int = 0
    """연속으로 NEGATIVE 감정이 감지된 턴 수.
    예: 2턴 연속 부정 → 적극 개입 전략(응답 방향 전환, 사과 삽입 등) 트리거."""


@dataclass
class StageLog:
    stage_id: str = ""
    input_text: str = ""
    output_text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    confidence: float = 1.0
    elapsed_ms: float = 0.0
    skipped: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineContext:
    """Mutable context that travels through the pipeline."""

    # --- Original inputs (immutable reference) ---
    original_user_prompt: str = ""
    original_system_prompt: str = ""

    # --- Current working text (mutated by stages) ---
    user_prompt: str = ""
    system_prompt: str = ""

    # --- Domain / Task ---
    domain: Domain = Domain.UNKNOWN
    domain_confidence: float = 0.0
    domain_params: dict[str, Any] = field(default_factory=dict)

    # --- Emotion ---
    emotion_layer: EmotionLayer = field(default_factory=EmotionLayer)

    # --- Ambiguity ---
    ambiguous_expressions: list[dict[str, Any]] = field(default_factory=list)

    # --- Session (multi-turn) ---
    session_id: str | None = None
    turn_index: int = 0

    # --- Compression settings ---
    compression_level: CompressionLevel = CompressionLevel.BALANCED
    target_model: str = "gpt-4o-mini"

    # --- Output strategy (populated by Stage10 / OutputStrategyEngine) ---
    output_strategy: dict[str, Any] = field(default_factory=dict)

    # --- PII mapping (for restore after LLM response) ---
    pii_mapping: dict[str, str] = field(default_factory=dict)

    # --- Pipeline execution trace ---
    stage_logs: list[StageLog] = field(default_factory=list)

    # --- Flags ---
    injection_detected: bool = False
    injection_risk_score: float = 0.0
    cache_hit: bool = False
    cached_response: str | None = None

    # --- Token counts ---
    original_input_tokens: int = 0
    compressed_input_tokens: int = 0

    # --- Misc metadata ---
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def token_savings_ratio(self) -> float:
        if self.original_input_tokens == 0:
            return 0.0
        return 1 - (self.compressed_input_tokens / self.original_input_tokens)
