"""Pydantic request / response models for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


# ── Request models ──────────────────────────────────────────────

class CompressRequest(BaseModel):
    user_prompt: str
    system_prompt: str = ""
    session_id: str | None = None
    target_model: str = "gpt-4o-mini"
    preset: str | None = None
    compression_level: str = "balanced"
    filter_overrides: dict[str, bool] | None = None


class ChatCompletionMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat/completions request."""
    model: str = "gpt-4o-mini"
    messages: list[ChatCompletionMessage]
    max_tokens: int | None = None
    temperature: float = 1.0
    stream: bool = False

    # PromptForge extensions (optional)
    pf_session_id: str | None = None
    pf_preset: str | None = None
    pf_compression_level: str = "balanced"
    pf_filter_overrides: dict[str, bool] | None = None


# ── Response models ─────────────────────────────────────────────

class StageLogResponse(BaseModel):
    stage_id: str
    confidence: float
    elapsed_ms: float
    skipped: bool
    gate_decision: str | None = None
    metadata: dict[str, Any] = {}


class TokenStats(BaseModel):
    original_tokens: int
    compressed_tokens: int
    savings_ratio: float
    savings_pct: str


class CostSavings(BaseModel):
    model: str
    cost_before_usd: float
    cost_after_usd: float
    savings_usd: float
    savings_pct: float


class CompressResponse(BaseModel):
    original_prompt: str
    compressed_prompt: str
    system_prompt: str = ""
    compressed_system_prompt: str = ""
    token_stats: TokenStats
    cost_savings: CostSavings | None = None
    quality_score: float | None = None
    domain: str = "unknown"
    emotion_layer: dict[str, Any] | None = None
    stage_logs: list[StageLogResponse] = []
    injection_detected: bool = False


class PipelineStatusResponse(BaseModel):
    stages: dict[str, dict[str, Any]]


class PresetListResponse(BaseModel):
    presets: list[str]


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
