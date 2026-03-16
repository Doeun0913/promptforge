"""Sentence embedding utilities.

Shared across multiple stages (S4, S5, semantic cache, etc.).
"""

from __future__ import annotations

import numpy as np


class EmbeddingModel:
    def __init__(
        self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ) -> None:
        self.model_name = model_name
        self._model = None

    async def load(self) -> None:
        # TODO: load sentence-transformers model
        pass

    async def encode(self, texts: list[str]) -> np.ndarray:
        # TODO: batch encoding
        return np.zeros((len(texts), 384))

    async def similarity(self, text_a: str, text_b: str) -> float:
        # TODO: cosine similarity between two texts
        return 0.0
