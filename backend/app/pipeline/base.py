"""Abstract base class for every pipeline stage."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .context import PipelineContext, StageLog

logger = logging.getLogger(__name__)


def _safe_count_tokens(text: str, model: str) -> int:
    """토큰 수 계산. 실패 시 0 반환 (스테이지 실행을 막지 않음)."""
    try:
        from app.utils.tokenizer import count_tokens
        return count_tokens(text, model)
    except Exception as exc:
        logger.debug("토큰 카운팅 실패 (%s): %s", model, exc)
        return 0


@dataclass
class StageResult:
    text: str
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseStage(ABC):
    """Every filter stage inherits from this class."""

    stage_id: str = "base"
    stage_name: str = "Base Stage"
    description: str = ""

    # Stages that modify semantics should set this to True
    # so the pipeline can route them through the Confidence Gate.
    modifies_semantics: bool = False

    def __init__(self) -> None:
        self._enabled = True

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    # ------------------------------------------------------------------
    # Public entry point – wraps process() with logging and timing
    # ------------------------------------------------------------------
    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        if not self._enabled:
            ctx.stage_logs.append(
                StageLog(stage_id=self.stage_id, skipped=True)
            )
            return ctx

        snapshot = ctx.user_prompt
        t0 = time.perf_counter()

        # ── 입력 토큰 카운팅 ──────────────────────────────────────────
        input_tokens = _safe_count_tokens(snapshot, ctx.target_model)

        result = await self.process(ctx)

        elapsed = (time.perf_counter() - t0) * 1000

        # ── 출력 토큰 카운팅 ──────────────────────────────────────────
        output_tokens = _safe_count_tokens(result.text, ctx.target_model)

        ctx.user_prompt = result.text
        ctx.stage_logs.append(
            StageLog(
                stage_id=self.stage_id,
                input_text=snapshot,
                output_text=result.text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                confidence=result.confidence,
                elapsed_ms=elapsed,
                metadata=result.metadata,
            )
        )
        return ctx

    @abstractmethod
    async def process(self, ctx: PipelineContext) -> StageResult:
        """Subclasses implement their transformation logic here."""
        ...

    def __repr__(self) -> str:
        status = "ON" if self._enabled else "OFF"
        return f"<{self.stage_name} [{status}]>"
