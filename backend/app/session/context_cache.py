"""Session-level context embedding cache for multi-turn deduplication."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class CachedContext:
    text: str
    embedding: np.ndarray
    turn_index: int


class ContextCache:
    """Sliding-window cache of sentence embeddings per session."""

    def __init__(self, window_size: int = 10) -> None:
        self.window_size = window_size
        self._cache: dict[str, list[CachedContext]] = {}

    def add(self, session_id: str, text: str, embedding: np.ndarray, turn_index: int) -> None:
        if session_id not in self._cache:
            self._cache[session_id] = []
        entries = self._cache[session_id]
        entries.append(CachedContext(text=text, embedding=embedding, turn_index=turn_index))
        if len(entries) > self.window_size:
            self._cache[session_id] = entries[-self.window_size:]

    def get_embeddings(self, session_id: str) -> list[CachedContext]:
        return self._cache.get(session_id, [])

    def clear(self, session_id: str) -> None:
        self._cache.pop(session_id, None)
