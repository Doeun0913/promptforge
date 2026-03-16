"""Basic pipeline integration tests."""

import asyncio
import pytest

from app.pipeline.context import PipelineContext
from app.pipeline.factory import create_pipeline


@pytest.fixture
def pipeline():
    return create_pipeline()


@pytest.mark.asyncio
async def test_pipeline_passthrough(pipeline):
    """With stub stages, text should pass through unchanged."""
    ctx = PipelineContext(user_prompt="안녕하세요 테스트입니다")
    result = await pipeline.run(ctx)

    assert result.user_prompt == "안녕하세요 테스트입니다"
    assert result.original_user_prompt == "안녕하세요 테스트입니다"
    assert len(result.stage_logs) > 0


@pytest.mark.asyncio
async def test_pipeline_stage_count(pipeline):
    """All 17 stages should be registered."""
    assert len(pipeline.filter_chain.all_stages) == 17


@pytest.mark.asyncio
async def test_pipeline_disable_stage(pipeline):
    """Disabling a stage should skip it."""
    pipeline.filter_chain.disable("s1_emotion")
    ctx = PipelineContext(user_prompt="테스트")
    result = await pipeline.run(ctx)

    emotion_log = next(
        (l for l in result.stage_logs if l.stage_id == "s1_emotion"), None
    )
    assert emotion_log is not None
    assert emotion_log.skipped is True


@pytest.mark.asyncio
async def test_pipeline_preset_application(pipeline):
    """Applying a preset should toggle stages correctly."""
    from app.modules.preset_manager import BUILTIN_PRESETS

    creative = BUILTIN_PRESETS["creative"]
    pipeline.filter_chain.apply_preset(creative)

    rewriter = pipeline.filter_chain.get_stage("s3_rewriter")
    assert rewriter is not None
    assert rewriter.enabled is False

    emotion = pipeline.filter_chain.get_stage("s1_emotion")
    assert emotion is not None
    assert emotion.enabled is True
