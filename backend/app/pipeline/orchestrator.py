"""Pipeline Orchestrator — 입력 필터 파이프라인 전체 실행."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from loguru import logger as loguru_logger

from .base import BaseStage, _safe_count_tokens
from .confidence_gate import ConfidenceGate, GateDecision
from .context import PipelineContext
from .filter_chain import FilterChainManager

if TYPE_CHECKING:
    from app.modules.semantic_verifier import SemanticVerifier

log = logging.getLogger(__name__)


def _safe_count_multi(text: str, model_ids: list[str]) -> dict:
    try:
        from app.utils.tokenizer import count_tokens_multi
        return count_tokens_multi(text, model_ids)
    except Exception as exc:
        log.debug("멀티모델 토큰 카운팅 실패: %s", exc)
        return {}


class PipelineOrchestrator:
    """
    실행 흐름:
    1. 원본 토큰 수 기록
    2. 스테이지 순회 → Gate → NLI 2차 검증
    3. 압축 후 토큰 수 + 멀티모델 비교
    """

    def __init__(
        self,
        filter_chain: FilterChainManager,
        confidence_gate: ConfidenceGate,
        semantic_verifier: "SemanticVerifier | None" = None,
    ) -> None:
        self.filter_chain = filter_chain
        self.confidence_gate = confidence_gate
        self._semantic_verifier = semantic_verifier

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        ctx.original_user_prompt = ctx.user_prompt
        ctx.original_system_prompt = ctx.system_prompt

        ctx.original_input_tokens = _safe_count_tokens(ctx.user_prompt, ctx.target_model)

        t0 = time.perf_counter()
        loguru_logger.info(
            "Pipeline start | stages={} | tokens={} | model={}",
            len(self.filter_chain.active_stages),
            ctx.original_input_tokens,
            ctx.target_model,
        )

        for stage in self.filter_chain.active_stages:
            ctx = await self._run_stage(stage, ctx)
            if ctx.injection_detected:
                loguru_logger.warning("Injection detected — halting pipeline.")
                break
            if ctx.cache_hit:
                loguru_logger.info("Semantic cache hit — skipping remaining stages.")
                break

        ctx.compressed_input_tokens = _safe_count_tokens(ctx.user_prompt, ctx.target_model)

        if ctx.compare_models:
            ctx.multi_model_tokens = _safe_count_multi(ctx.user_prompt, ctx.compare_models)

        elapsed = (time.perf_counter() - t0) * 1000
        loguru_logger.info(
            "Pipeline done | elapsed={:.1f}ms | tokens: {} → {} | savings={:.1%}",
            elapsed,
            ctx.original_input_tokens,
            ctx.compressed_input_tokens,
            ctx.token_savings_ratio,
        )
        return ctx

    async def _run_stage(self, stage: BaseStage, ctx: PipelineContext) -> PipelineContext:
        snapshot = ctx.user_prompt
        ctx = await stage.execute(ctx)

        if not (stage.modifies_semantics and ctx.stage_logs):
            return ctx

        last_log = ctx.stage_logs[-1]
        if last_log.skipped:
            return ctx

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
            last_log.metadata["gate_decision"] = "ask_user"

        elif verdict.decision == GateDecision.ACCEPT:
            if self._semantic_verifier and snapshot != ctx.user_prompt:
                nli = await self._semantic_verifier.verify(snapshot, ctx.user_prompt)
                last_log.metadata.update({
                    "gate_decision": "accepted" if nli.is_equivalent else "nli_rejected",
                    "nli_forward": nli.forward_score,
                    "nli_backward": nli.backward_score,
                    "nli_equivalent": nli.is_equivalent,
                    "nli_skipped": nli.skipped,
                })
                if not nli.is_equivalent:
                    ctx.user_prompt = snapshot
                    log.debug("NLI REJECT: stage=%s fw=%.3f bw=%.3f",
                              stage.stage_id, nli.forward_score, nli.backward_score)
            else:
                last_log.metadata["gate_decision"] = "accepted"

        return ctx
