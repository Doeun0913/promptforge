"""Filter Chain Manager – controls which stages are active and their order."""

from __future__ import annotations

from typing import Any

from .base import BaseStage


class FilterChainManager:
    """Manages an ordered list of pipeline stages with ON/OFF toggling."""

    def __init__(self) -> None:
        self._stages: list[BaseStage] = []
        self._stage_map: dict[str, BaseStage] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    def register(self, stage: BaseStage) -> None:
        self._stages.append(stage)
        self._stage_map[stage.stage_id] = stage

    def register_many(self, stages: list[BaseStage]) -> None:
        for s in stages:
            self.register(s)

    # ------------------------------------------------------------------
    # Toggle
    # ------------------------------------------------------------------
    def enable(self, stage_id: str) -> None:
        if stage_id in self._stage_map:
            self._stage_map[stage_id].enabled = True

    def disable(self, stage_id: str) -> None:
        if stage_id in self._stage_map:
            self._stage_map[stage_id].enabled = False

    def set_enabled(self, stage_id: str, enabled: bool) -> None:
        if stage_id in self._stage_map:
            self._stage_map[stage_id].enabled = enabled

    def apply_preset(self, preset: dict[str, bool]) -> None:
        """Apply a preset: ``{"stage_id": True/False, ...}``."""
        for stage_id, enabled in preset.items():
            self.set_enabled(stage_id, enabled)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------
    @property
    def active_stages(self) -> list[BaseStage]:
        return [s for s in self._stages if s.enabled]

    @property
    def all_stages(self) -> list[BaseStage]:
        return list(self._stages)

    def get_stage(self, stage_id: str) -> BaseStage | None:
        return self._stage_map.get(stage_id)

    def get_status(self) -> dict[str, dict[str, Any]]:
        return {
            s.stage_id: {
                "name": s.stage_name,
                "enabled": s.enabled,
                "modifies_semantics": s.modifies_semantics,
            }
            for s in self._stages
        }

    def __len__(self) -> int:
        return len(self._stages)

    def __repr__(self) -> str:
        active = len(self.active_stages)
        total = len(self._stages)
        return f"<FilterChainManager {active}/{total} active>"
