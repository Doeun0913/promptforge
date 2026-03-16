"""Preset Manager – predefined and custom filter chain configurations."""

from __future__ import annotations

from typing import Any

BUILTIN_PRESETS: dict[str, dict[str, bool]] = {
    "coding": {
        "s0_domain": True,
        "s0b_korean": True,
        "s1_emotion": False,
        "s2_ambiguity": True,
        "s3_rewriter": True,
        "s4_multiturn": True,
        "s5_redundancy": True,
        "s6_verbosity": True,
        "s7_condenser": True,
        "s8_noise": True,
        "s9_structurer": True,
        "s10_output": True,
        "s11_system": True,
        "s12_pii": True,
        "s13_injection": True,
        "s14_lang": False,
        "s15_tokenizer": True,
    },
    "creative": {
        "s0_domain": True,
        "s0b_korean": True,
        "s1_emotion": True,
        "s2_ambiguity": False,
        "s3_rewriter": False,
        "s4_multiturn": True,
        "s5_redundancy": False,
        "s6_verbosity": False,
        "s7_condenser": False,
        "s8_noise": True,
        "s9_structurer": False,
        "s10_output": True,
        "s11_system": True,
        "s12_pii": True,
        "s13_injection": True,
        "s14_lang": False,
        "s15_tokenizer": False,
    },
    "academic": {
        "s0_domain": True,
        "s0b_korean": True,
        "s1_emotion": False,
        "s2_ambiguity": True,
        "s3_rewriter": True,
        "s4_multiturn": True,
        "s5_redundancy": True,
        "s6_verbosity": True,
        "s7_condenser": True,
        "s8_noise": True,
        "s9_structurer": True,
        "s10_output": True,
        "s11_system": True,
        "s12_pii": True,
        "s13_injection": True,
        "s14_lang": True,
        "s15_tokenizer": True,
    },
    "casual": {
        "s0_domain": True,
        "s0b_korean": True,
        "s1_emotion": True,
        "s2_ambiguity": True,
        "s3_rewriter": True,
        "s4_multiturn": True,
        "s5_redundancy": True,
        "s6_verbosity": True,
        "s7_condenser": True,
        "s8_noise": True,
        "s9_structurer": True,
        "s10_output": True,
        "s11_system": True,
        "s12_pii": True,
        "s13_injection": True,
        "s14_lang": True,
        "s15_tokenizer": True,
    },
}


class PresetManager:
    def __init__(self) -> None:
        self._custom_presets: dict[str, dict[str, bool]] = {}

    def get_preset(self, name: str) -> dict[str, bool] | None:
        if name in BUILTIN_PRESETS:
            return BUILTIN_PRESETS[name]
        return self._custom_presets.get(name)

    def save_custom(self, name: str, config: dict[str, bool]) -> None:
        self._custom_presets[name] = config

    def list_presets(self) -> list[str]:
        return list(BUILTIN_PRESETS.keys()) + list(self._custom_presets.keys())
