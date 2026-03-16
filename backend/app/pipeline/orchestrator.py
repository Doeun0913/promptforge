"""Pipeline Orchestrator – runs the full input filter pipeline."""

from __future__ import annotations

import time
from typing import Any

from loguru import logger

from .base import BaseStage, StageResult
from .confidence_gate import ConfidenceGate, GateDecision
from .context import PipelineContext
from .filter_chain import FilterChainManager


class PipelineOrchestrator:
    """
    Runs the input-side filter pipeline.

    Responsibilities:
    1. Walk through active stages in order.
    2. Route semantic-modifying stages through the ConfidenceGate.
    3. Collect per-stage logs into PipelineContext.
    """

    def __init__(
        self,
        filter_chain: FilterChainManager,
        confidence_gate: ConfidenceGate,
    ) -> None:
        self.filter_chain = filter_chain
        self.confidence_gate = confidence_gate

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        ctx.original_user_prompt = ctx.user_prompt
        ctx.original_system_prompt = ctx.system_prompt

        t0 = time.perf_counter()
        logger.info(
            "Pipeline start | stages={} | prompt_len={}",
            len(self.filter_chain.active_stages),
            len(ctx.user_prompt),
        )

        for stage in self.filter_chain.active_stages:
            ctx = await self._run_stage(stage, ctx)

            if ctx.injection_detected:
                logger.warning("Injection detected – halting pipeline.")
                break

            if ctx.cache_hit:
                logger.info("Semantic cache hit – skipping remaining stages.")
                break

        elapsed = (time.perf_counter() - t0) * 1000
        logger.info(
            "Pipeline done | elapsed={:.1f}ms | savings={:.1%}",
            elapsed,
            ctx.token_savings_ratio,
        )
        return ctx

    async def _run_stage(
        self, stage: BaseStage, ctx: PipelineContext
    ) -> PipelineContext:
        snapshot = ctx.user_prompt

        ctx = await stage.execute(ctx)

        if stage.modifies_semantics and ctx.stage_logs:
            last_log = ctx.stage_logs[-1]
            if not last_log.skipped:
                verdict = self.confidence_gate.evaluate(
                    confidence=last_log.confidence,
                    stage_id=stage.stage_id,
                    original_text=snapshot,
                    transformed_text=ctx.user_prompt,
                )
                if verdict.decision == GateDecision.REJECT:
                    ctx.user_prompt = snapshot
                    last_log.metadata["gate_decision"] = "rejected"
                elif verdict.decision == GateDecision.ASK_USER:
                    # In async/API mode, we keep the transformed text for now
                    # but flag it for user review.
                    last_log.metadata["gate_decision"] = "ask_user"
                else:
                    last_log.metadata["gate_decision"] = "accepted"

        return ctx
