"""Latency Manager – controls lightweight vs. full pipeline execution."""

from __future__ import annotations

LIGHTWEIGHT_STAGES = {"s0b_korean", "s6_verbosity", "s7_condenser", "s8_noise", "s12_pii"}


class LatencyManager:
    def __init__(self, mode: str = "full") -> None:
        self.mode = mode  # "lightweight" | "full"

    def should_skip(self, stage_id: str) -> bool:
        if self.mode == "lightweight":
            return stage_id not in LIGHTWEIGHT_STAGES
        return False

    def get_parallelizable_groups(self) -> list[list[str]]:
        """Returns groups of stages that can run in parallel."""
        # TODO: dependency analysis for parallel execution
        return []
