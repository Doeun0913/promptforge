"""Pipeline factory – convenience function to wire up the full pipeline."""

from __future__ import annotations

from .confidence_gate import ConfidenceGate, GateMode
from .filter_chain import FilterChainManager
from .orchestrator import PipelineOrchestrator

from .stage0_domain import DomainClassifierStage
from .stage0b_korean_preprocess import KoreanPreprocessStage
from .stage1_emotion import EmotionSeparatorStage
from .stage2_ambiguity import AmbiguityDetectorStage
from .stage3_rewriter import IntentRewriterStage
from .stage4_multiturn import MultiTurnDeduplicatorStage
from .stage5_redundancy import RedundancyEliminatorStage
from .stage6_verbosity import VerbosityCompressorStage
from .stage7_phrase_condenser import PhraseCondenserStage
from .stage8_noise import NoiseFilterStage
from .stage9_structurer import PromptStructurerStage
from .stage10_output_optimizer import OutputOptimizerStage
from .stage11_system_prompt import SystemPromptOptimizerStage
from .stage12_pii_masker import PIIMaskerStage
from .stage13_injection import InjectionDetectorStage
from .stage14_lang_norm import LanguageNormalizerStage
from .stage15_tokenizer_aware import TokenizerAwareCompressorStage

ALL_STAGES = [
    DomainClassifierStage,
    KoreanPreprocessStage,
    EmotionSeparatorStage,
    AmbiguityDetectorStage,
    IntentRewriterStage,
    MultiTurnDeduplicatorStage,
    RedundancyEliminatorStage,
    VerbosityCompressorStage,
    PhraseCondenserStage,
    NoiseFilterStage,
    PromptStructurerStage,
    OutputOptimizerStage,
    SystemPromptOptimizerStage,
    PIIMaskerStage,
    InjectionDetectorStage,
    LanguageNormalizerStage,
    TokenizerAwareCompressorStage,
]


def create_pipeline(
    gate_mode: GateMode = GateMode.AUTO,
    auto_threshold: float = 0.95,
) -> PipelineOrchestrator:
    """Instantiate a fully-wired pipeline with all stages registered."""

    chain = FilterChainManager()
    chain.register_many([cls() for cls in ALL_STAGES])

    gate = ConfidenceGate(mode=gate_mode, auto_threshold=auto_threshold)

    return PipelineOrchestrator(filter_chain=chain, confidence_gate=gate)
