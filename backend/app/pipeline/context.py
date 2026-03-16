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


@dataclass
class EmotionLayer:
    emotions: list[str] = field(default_factory=list)
    confidence: float = 0.0
    expressions: list[str] = field(default_factory=list)


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
