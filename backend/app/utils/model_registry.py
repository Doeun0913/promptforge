"""Multi-model registry — tokenizer types, pricing, context windows.

6개 프로바이더 20개+ 모델의 토크나이저 종류, 입출력 가격, 컨텍스트 윈도우를 등록한다.

토크나이저 전략
--------------
tiktoken       : OpenAI, DeepSeek — tiktoken 라이브러리 직접 사용
cl100k_approx  : Claude, Gemini   — cl100k_base 근사 (공식 토크나이저 비공개)
hf_approx      : Llama, Mistral   — cl100k_base 근사 (HF 모델 로드 없이 빠른 추정)
                 Phase 2에서 transformers.AutoTokenizer lazy load로 교체 예정

가격 정보 (USD / 1K tokens, 2025년 3월 기준)
입력 가격은 input_price_per_1k, 출력 가격은 output_price_per_1k.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TokenizerType = Literal["tiktoken", "cl100k_approx", "hf_approx"]


@dataclass(frozen=True)
class ModelInfo:
    provider: str
    """프로바이더 식별자. "openai" | "anthropic" | "google" | "meta" | "mistral" | "deepseek" """

    model_id: str
    """API 호출 시 사용하는 모델 ID. 예: "gpt-4o-mini" """

    display_name: str
    """사람이 읽기 좋은 모델명. 예: "GPT-4o Mini" """

    tokenizer_type: TokenizerType
    """토크나이저 종류."""

    tokenizer_id: str
    """tiktoken 인코딩명 또는 HF 모델 ID."""

    input_price_per_1k: float
    """입력 토큰 1K당 가격 (USD)."""

    output_price_per_1k: float
    """출력 토큰 1K당 가격 (USD)."""

    context_window: int
    """최대 컨텍스트 크기 (토큰 수)."""


# ── 모델 레지스트리 ───────────────────────────────────────────────────────

_REGISTRY: list[ModelInfo] = [

    # ── OpenAI ────────────────────────────────────────────────────────────
    ModelInfo(
        provider="openai", model_id="gpt-4o",
        display_name="GPT-4o",
        tokenizer_type="tiktoken", tokenizer_id="gpt-4o",
        input_price_per_1k=0.005, output_price_per_1k=0.015,
        context_window=128_000,
    ),
    ModelInfo(
        provider="openai", model_id="gpt-4o-mini",
        display_name="GPT-4o Mini",
        tokenizer_type="tiktoken", tokenizer_id="gpt-4o-mini",
        input_price_per_1k=0.000150, output_price_per_1k=0.000600,
        context_window=128_000,
    ),
    ModelInfo(
        provider="openai", model_id="gpt-4-turbo",
        display_name="GPT-4 Turbo",
        tokenizer_type="tiktoken", tokenizer_id="gpt-4-turbo",
        input_price_per_1k=0.010, output_price_per_1k=0.030,
        context_window=128_000,
    ),
    ModelInfo(
        provider="openai", model_id="gpt-3.5-turbo",
        display_name="GPT-3.5 Turbo",
        tokenizer_type="tiktoken", tokenizer_id="gpt-3.5-turbo",
        input_price_per_1k=0.000500, output_price_per_1k=0.001500,
        context_window=16_385,
    ),
    ModelInfo(
        provider="openai", model_id="o1",
        display_name="o1",
        tokenizer_type="tiktoken", tokenizer_id="o1",
        input_price_per_1k=0.015, output_price_per_1k=0.060,
        context_window=200_000,
    ),
    ModelInfo(
        provider="openai", model_id="o3-mini",
        display_name="o3-mini",
        tokenizer_type="tiktoken", tokenizer_id="o3-mini",
        input_price_per_1k=0.001100, output_price_per_1k=0.004400,
        context_window=200_000,
    ),

    # ── Anthropic Claude ──────────────────────────────────────────────────
    ModelInfo(
        provider="anthropic", model_id="claude-3-5-sonnet-20241022",
        display_name="Claude 3.5 Sonnet",
        tokenizer_type="cl100k_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.003, output_price_per_1k=0.015,
        context_window=200_000,
    ),
    ModelInfo(
        provider="anthropic", model_id="claude-3-haiku-20240307",
        display_name="Claude 3 Haiku",
        tokenizer_type="cl100k_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.000250, output_price_per_1k=0.001250,
        context_window=200_000,
    ),
    ModelInfo(
        provider="anthropic", model_id="claude-3-opus-20240229",
        display_name="Claude 3 Opus",
        tokenizer_type="cl100k_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.015, output_price_per_1k=0.075,
        context_window=200_000,
    ),

    # ── Google Gemini ─────────────────────────────────────────────────────
    ModelInfo(
        provider="google", model_id="gemini-1.5-pro",
        display_name="Gemini 1.5 Pro",
        tokenizer_type="cl100k_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.003500, output_price_per_1k=0.010500,
        context_window=2_000_000,
    ),
    ModelInfo(
        provider="google", model_id="gemini-1.5-flash",
        display_name="Gemini 1.5 Flash",
        tokenizer_type="cl100k_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.000075, output_price_per_1k=0.000300,
        context_window=1_000_000,
    ),
    ModelInfo(
        provider="google", model_id="gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        tokenizer_type="cl100k_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.000100, output_price_per_1k=0.000400,
        context_window=1_000_000,
    ),

    # ── Meta Llama ────────────────────────────────────────────────────────
    # 가격은 Groq / Together AI 기준 (자체 호스팅 시 $0)
    ModelInfo(
        provider="meta", model_id="llama-3.1-70b-versatile",
        display_name="Llama 3.1 70B",
        tokenizer_type="hf_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.000590, output_price_per_1k=0.000790,
        context_window=131_072,
    ),
    ModelInfo(
        provider="meta", model_id="llama-3.1-8b-instant",
        display_name="Llama 3.1 8B",
        tokenizer_type="hf_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.000050, output_price_per_1k=0.000080,
        context_window=131_072,
    ),

    # ── Mistral ───────────────────────────────────────────────────────────
    ModelInfo(
        provider="mistral", model_id="mistral-large-latest",
        display_name="Mistral Large",
        tokenizer_type="hf_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.002, output_price_per_1k=0.006,
        context_window=131_072,
    ),
    ModelInfo(
        provider="mistral", model_id="mistral-small-latest",
        display_name="Mistral Small",
        tokenizer_type="hf_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.000200, output_price_per_1k=0.000600,
        context_window=32_768,
    ),
    ModelInfo(
        provider="mistral", model_id="open-mixtral-8x7b",
        display_name="Mixtral 8x7B",
        tokenizer_type="hf_approx", tokenizer_id="cl100k_base",
        input_price_per_1k=0.000700, output_price_per_1k=0.000700,
        context_window=32_768,
    ),

    # ── DeepSeek ──────────────────────────────────────────────────────────
    ModelInfo(
        provider="deepseek", model_id="deepseek-chat",
        display_name="DeepSeek V3",
        tokenizer_type="tiktoken", tokenizer_id="cl100k_base",
        input_price_per_1k=0.000270, output_price_per_1k=0.001100,
        context_window=64_000,
    ),
    ModelInfo(
        provider="deepseek", model_id="deepseek-coder",
        display_name="DeepSeek Coder",
        tokenizer_type="tiktoken", tokenizer_id="cl100k_base",
        input_price_per_1k=0.000140, output_price_per_1k=0.000280,
        context_window=64_000,
    ),
]

# ── 조회 인덱스 ───────────────────────────────────────────────────────────

_BY_ID: dict[str, ModelInfo] = {m.model_id: m for m in _REGISTRY}
_BY_PROVIDER: dict[str, list[ModelInfo]] = {}
for _m in _REGISTRY:
    _BY_PROVIDER.setdefault(_m.provider, []).append(_m)


# ── 공개 API ─────────────────────────────────────────────────────────────

def get_model(model_id: str) -> ModelInfo | None:
    """모델 ID로 ModelInfo 반환. 미등록 모델이면 None."""
    return _BY_ID.get(model_id)


def get_model_or_default(model_id: str, default_id: str = "gpt-4o-mini") -> ModelInfo:
    """모델 ID로 조회; 없으면 default_id 반환."""
    return _BY_ID.get(model_id) or _BY_ID[default_id]


def list_models(provider: str | None = None) -> list[ModelInfo]:
    """전체 또는 특정 프로바이더의 모델 목록 반환."""
    if provider:
        return list(_BY_PROVIDER.get(provider, []))
    return list(_REGISTRY)


def all_model_ids() -> list[str]:
    """등록된 모든 model_id 목록."""
    return list(_BY_ID.keys())
