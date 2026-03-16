"""Token-level classifier for tokenizer-aware compression.

Assigns a preservation probability to each token (LLMLingua-2 style).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TokenClassification:
    tokens: list[str]
    preservation_probs: list[float]


class TokenClassifierModel:
    def __init__(self, model_name: str = "xlm-roberta-base") -> None:
        self.model_name = model_name
        self._model = None

    async def load(self) -> None:
        # TODO: load fine-tuned XLM-RoBERTa token classifier
        pass

    async def classify(self, text: str) -> TokenClassification:
        # TODO: token-level classification
        return TokenClassification(tokens=[], preservation_probs=[])
