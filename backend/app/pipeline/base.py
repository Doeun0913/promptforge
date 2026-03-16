"""Abstract base class for every pipeline stage."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .context import PipelineContext, StageLog


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

        result = await self.process(ctx)

        elapsed = (time.perf_counter() - t0) * 1000

        ctx.user_prompt = result.text
        ctx.stage_logs.append(
            StageLog(
                stage_id=self.stage_id,
                input_text=snapshot,
                output_text=result.text,
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
