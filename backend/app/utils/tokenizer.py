"""Token counting utilities – supports multiple tokenizers."""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=8)
def _get_tiktoken_encoding(model: str):
    import tiktoken
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    enc = _get_tiktoken_encoding(model)
    return len(enc.encode(text))


def tokenize(text: str, model: str = "gpt-4o-mini") -> list[str]:
    enc = _get_tiktoken_encoding(model)
    token_ids = enc.encode(text)
    return [enc.decode([tid]) for tid in token_ids]


def pick_shortest_token_expression(
    candidates: list[str], model: str = "gpt-4o-mini"
) -> str:
    """Given synonym candidates, return the one with fewest tokens."""
    if not candidates:
        return ""
    return min(candidates, key=lambda c: count_tokens(c, model))
