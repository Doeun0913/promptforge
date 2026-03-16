"""API routes – compress endpoint + OpenAI-compatible proxy + management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .schemas import (
    ChatCompletionRequest,
    CompressRequest,
    CompressResponse,
    HealthResponse,
    PipelineStatusResponse,
    PresetListResponse,
    StageLogResponse,
    TokenStats,
)
from ..api.deps import get_orchestrator, get_filter_chain, get_preset_manager

router = APIRouter()


# ── Health ───────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


# ── Compress (demo / standalone) ─────────────────────────────────

@router.post("/v1/compress", response_model=CompressResponse)
async def compress(req: CompressRequest):
    from ..pipeline.context import PipelineContext, CompressionLevel

    orchestrator = get_orchestrator()

    ctx = PipelineContext(
        user_prompt=req.user_prompt,
        system_prompt=req.system_prompt,
        target_model=req.target_model,
        compression_level=CompressionLevel(req.compression_level),
    )

    if req.session_id:
        ctx.session_id = req.session_id

    if req.preset:
        preset_mgr = get_preset_manager()
        preset_config = preset_mgr.get_preset(req.preset)
        if preset_config:
            orchestrator.filter_chain.apply_preset(preset_config)

    if req.filter_overrides:
        orchestrator.filter_chain.apply_preset(req.filter_overrides)

    ctx = await orchestrator.run(ctx)

    stage_logs = [
        StageLogResponse(
            stage_id=log.stage_id,
            confidence=log.confidence,
            elapsed_ms=log.elapsed_ms,
            skipped=log.skipped,
            gate_decision=log.metadata.get("gate_decision"),
            metadata=log.metadata,
        )
        for log in ctx.stage_logs
    ]

    original_tokens = len(ctx.original_user_prompt.split())
    compressed_tokens = len(ctx.user_prompt.split())
    savings = 1 - (compressed_tokens / max(original_tokens, 1))

    return CompressResponse(
        original_prompt=ctx.original_user_prompt,
        compressed_prompt=ctx.user_prompt,
        system_prompt=ctx.original_system_prompt,
        compressed_system_prompt=ctx.system_prompt,
        token_stats=TokenStats(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            savings_ratio=savings,
            savings_pct=f"{savings:.1%}",
        ),
        domain=ctx.domain.value,
        emotion_layer={
            "emotions": ctx.emotion_layer.emotions,
            "confidence": ctx.emotion_layer.confidence,
        },
        stage_logs=stage_logs,
        injection_detected=ctx.injection_detected,
    )


# ── OpenAI-compatible proxy (Phase 5) ────────────────────────────

@router.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    # TODO: Phase 5 – full proxy implementation
    # 1. Extract system & user prompts from messages
    # 2. Run input pipeline
    # 3. Forward to target LLM
    # 4. Run output post-filter
    # 5. Return OpenAI-compatible response
    raise HTTPException(501, detail="Proxy endpoint not yet implemented")


# ── Pipeline management ──────────────────────────────────────────

@router.get("/v1/pipeline/status", response_model=PipelineStatusResponse)
async def pipeline_status():
    chain = get_filter_chain()
    return PipelineStatusResponse(stages=chain.get_status())


@router.get("/v1/presets", response_model=PresetListResponse)
async def list_presets():
    mgr = get_preset_manager()
    return PresetListResponse(presets=mgr.list_presets())


@router.post("/v1/pipeline/toggle/{stage_id}")
async def toggle_stage(stage_id: str, enabled: bool = True):
    chain = get_filter_chain()
    stage = chain.get_stage(stage_id)
    if stage is None:
        raise HTTPException(404, detail=f"Stage '{stage_id}' not found")
    stage.enabled = enabled
    return {"stage_id": stage_id, "enabled": enabled}
