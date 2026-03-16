"""Evaluation metrics utilities."""

from __future__ import annotations


def token_savings_ratio(original_tokens: int, compressed_tokens: int) -> float:
    if original_tokens == 0:
        return 0.0
    return 1.0 - (compressed_tokens / original_tokens)


def compression_ratio(original_len: int, compressed_len: int) -> float:
    if original_len == 0:
        return 1.0
    return compressed_len / original_len


async def compute_semantic_similarity(text_a: str, text_b: str) -> float:
    # TODO: use EmbeddingModel for real similarity
    return 1.0


async def compute_bertscore(reference: str, candidate: str) -> dict[str, float]:
    # TODO: integrate bert_score library
    return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
