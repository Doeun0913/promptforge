"""Token counting utilities — multi-model support.

지원 토크나이저 전략
--------------------
tiktoken      : OpenAI(gpt-4o 등), DeepSeek — 정확
cl100k_approx : Claude, Gemini — cl100k_base 근사 (±5% 오차)
hf_approx     : Llama, Mistral — cl100k_base 근사 (±10% 오차)
               Phase 2에서 transformers.AutoTokenizer lazy-load로 교체 예정

비용 계산
---------
count_cost(tokens, model_id) → CostResult(input_cost_usd, ...)
count_tokens_multi(text, model_ids) → dict[model_id, ModelTokenResult]
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


# ── 데이터 구조 ───────────────────────────────────────────────────────────


@dataclass
class ModelTokenResult:
    """단일 모델의 토큰 수 + 비용 결과."""

    model_id: str
    input_tokens: int
    output_tokens: int = 0           # 압축 후 비교 시 채워짐
    input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0

    @property
    def total_cost_usd(self) -> float:
        return self.input_cost_usd + self.output_cost_usd

    @property
    def display_input_cost(self) -> str:
        """달러 소수점 6자리 표현. 예: "$0.000150" """
        return f"${self.input_cost_usd:.6f}"


# ── tiktoken 캐시 ─────────────────────────────────────────────────────────


@lru_cache(maxsize=16)
def _get_tiktoken_encoding(encoding_id: str):
    """tiktoken 인코딩 객체를 캐시해서 반환."""
    import tiktoken  # type: ignore
    try:
        return tiktoken.encoding_for_model(encoding_id)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


# ── 내부 카운터 ───────────────────────────────────────────────────────────


def _count_tiktoken(text: str, encoding_id: str) -> int:
    enc = _get_tiktoken_encoding(encoding_id)
    return len(enc.encode(text))


def _count_cl100k_approx(text: str) -> int:
    """cl100k_base 근사. Claude·Gemini 계열에 사용."""
    return _count_tiktoken(text, "cl100k_base")


def _count_hf_approx(text: str) -> int:
    """HF 토크나이저 근사 (cl100k_base). Llama·Mistral에 사용.

    Phase 2에서 transformers.AutoTokenizer로 교체:
        enc = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B")
        return len(enc.encode(text))
    """
    return _count_tiktoken(text, "cl100k_base")


# ── 공개 API ─────────────────────────────────────────────────────────────


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """단일 모델에 대한 토큰 수 반환.

    model_registry에 없는 모델은 cl100k_base 근사를 사용한다.
    """
    from app.utils.model_registry import get_model

    info = get_model(model)
    if info is None:
        return _count_cl100k_approx(text)

    if info.tokenizer_type == "tiktoken":
        return _count_tiktoken(text, info.tokenizer_id)
    else:
        # cl100k_approx / hf_approx 모두 동일 구현 (Phase 2에서 분기)
        return _count_cl100k_approx(text)


def count_cost(tokens: int, model_id: str, is_output: bool = False) -> float:
    """토큰 수 × 모델 단가 → USD 비용."""
    from app.utils.model_registry import get_model_or_default

    info = get_model_or_default(model_id)
    price = info.output_price_per_1k if is_output else info.input_price_per_1k
    return tokens * price / 1000.0


def count_tokens_with_cost(
    text: str,
    model_id: str,
    output_text: str = "",
) -> ModelTokenResult:
    """입력(+선택적 출력) 텍스트의 토큰 수와 비용을 한 번에 계산."""
    input_tokens = count_tokens(text, model_id)
    output_tokens = count_tokens(output_text, model_id) if output_text else 0

    return ModelTokenResult(
        model_id=model_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost_usd=count_cost(input_tokens, model_id, is_output=False),
        output_cost_usd=count_cost(output_tokens, model_id, is_output=True),
    )


def count_tokens_multi(
    text: str,
    model_ids: list[str],
    output_text: str = "",
) -> dict[str, ModelTokenResult]:
    """여러 모델에 대해 동시에 토큰 수 + 비용 계산.

    Args:
        text:       입력 텍스트 (압축 전 또는 후)
        model_ids:  비교할 모델 ID 목록
        output_text: 출력 텍스트 (비어 있으면 입력 비용만 계산)

    Returns:
        {model_id: ModelTokenResult} 딕셔너리
    """
    return {
        mid: count_tokens_with_cost(text, mid, output_text)
        for mid in model_ids
    }


# ── 기존 API 유지 (하위 호환) ─────────────────────────────────────────────


def tokenize(text: str, model: str = "gpt-4o-mini") -> list[str]:
    """토큰 문자열 목록 반환 (tiktoken 계열만 정확, 나머지 근사)."""
    from app.utils.model_registry import get_model

    info = get_model(model)
    enc_id = info.tokenizer_id if (info and info.tokenizer_type == "tiktoken") else "cl100k_base"
    enc = _get_tiktoken_encoding(enc_id)
    token_ids = enc.encode(text)
    return [enc.decode([tid]) for tid in token_ids]


def pick_shortest_token_expression(
    candidates: list[str], model: str = "gpt-4o-mini"
) -> str:
    """동의어 후보 중 토큰 수가 가장 적은 표현 반환."""
    if not candidates:
        return ""
    return min(candidates, key=lambda c: count_tokens(c, model))
