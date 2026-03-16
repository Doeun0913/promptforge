"""LLM Proxy – unified interface for calling OpenAI / Anthropic / etc."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator


@dataclass
class LLMRequest:
    model: str
    messages: list[dict[str, str]]
    max_tokens: int | None = None
    temperature: float = 1.0
    stream: bool = False
    response_format: dict[str, Any] | None = None
    extra_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str = "stop"


class LLMProxy:
    """Transparent proxy that forwards requests to the target LLM API."""

    def __init__(self) -> None:
        self._client = None

    async def call(self, request: LLMRequest) -> LLMResponse:
        # TODO: implement OpenAI / Anthropic API calls via httpx
        return LLMResponse(text="", model=request.model)

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        # TODO: SSE streaming proxy implementation
        yield ""
