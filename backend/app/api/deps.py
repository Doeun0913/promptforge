"""Dependency injection – singleton instances shared across the app."""

from __future__ import annotations

from functools import lru_cache

from ..pipeline.orchestrator import PipelineOrchestrator
from ..pipeline.filter_chain import FilterChainManager
from ..pipeline.confidence_gate import ConfidenceGate, GateMode
from ..modules.preset_manager import PresetManager

from ..pipeline.stage0_domain import DomainClassifierStage
from ..pipeline.stage0b_korean_preprocess import KoreanPreprocessStage
from ..pipeline.stage1_emotion import EmotionSeparatorStage
from ..pipeline.stage2_ambiguity import AmbiguityDetectorStage
from ..pipeline.stage3_rewriter import IntentRewriterStage
from ..pipeline.stage4_multiturn import MultiTurnDeduplicatorStage
from ..pipeline.stage5_redundancy import RedundancyEliminatorStage
from ..pipeline.stage6_verbosity import VerbosityCompressorStage
from ..pipeline.stage7_phrase_condenser import PhraseCondenserStage
from ..pipeline.stage8_noise import NoiseFilterStage
from ..pipeline.stage9_structurer import PromptStructurerStage
from ..pipeline.stage10_output_optimizer import OutputOptimizerStage
from ..pipeline.stage11_system_prompt import SystemPromptOptimizerStage
from ..pipeline.stage12_pii_masker import PIIMaskerStage
from ..pipeline.stage13_injection import InjectionDetectorStage
from ..pipeline.stage14_lang_norm import LanguageNormalizerStage
from ..pipeline.stage15_tokenizer_aware import TokenizerAwareCompressorStage


@lru_cache
def get_filter_chain() -> FilterChainManager:
    chain = FilterChainManager()
    chain.register_many([
        DomainClassifierStage(),
        KoreanPreprocessStage(),
        EmotionSeparatorStage(),
        AmbiguityDetectorStage(),
        IntentRewriterStage(),
        MultiTurnDeduplicatorStage(),
        RedundancyEliminatorStage(),
        VerbosityCompressorStage(),
        PhraseCondenserStage(),
        NoiseFilterStage(),
        PromptStructurerStage(),
        OutputOptimizerStage(),
        SystemPromptOptimizerStage(),
        PIIMaskerStage(),
        InjectionDetectorStage(),
        LanguageNormalizerStage(),
        TokenizerAwareCompressorStage(),
    ])
    return chain


@lru_cache
def get_confidence_gate() -> ConfidenceGate:
    return ConfidenceGate(mode=GateMode.AUTO)


@lru_cache
def get_orchestrator() -> PipelineOrchestrator:
    return PipelineOrchestrator(
        filter_chain=get_filter_chain(),
        confidence_gate=get_confidence_gate(),
    )


@lru_cache
def get_preset_manager() -> PresetManager:
    return PresetManager()
