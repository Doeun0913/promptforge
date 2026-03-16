"""OF1: Preamble / Epilogue Remover.

Strips generic LLM pleasantries from the beginning and end of responses.
"""

from __future__ import annotations


class PreambleRemover:
    async def process(self, text: str) -> str:
        # TODO: LLM response pattern dictionary
        # TODO: position-based rules (first/last sentence filtering)
        return text
