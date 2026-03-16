"""Feedback Loop – tracks filter results vs. LLM response quality."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FeedbackEntry:
    session_id: str
    original_prompt: str
    filtered_prompt: str
    response_text: str
    user_rating: int | None = None  # 1-5
    token_savings: float = 0.0
    filter_config: dict[str, Any] = field(default_factory=dict)


class FeedbackCollector:
    def __init__(self) -> None:
        self._history: list[FeedbackEntry] = []

    async def record(self, entry: FeedbackEntry) -> None:
        # TODO: persist to database
        self._history.append(entry)

    async def get_optimal_config(self, user_id: str) -> dict[str, Any]:
        # TODO: analyse history and recommend optimal filter settings
        return {}
