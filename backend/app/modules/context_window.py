"""Context Window Awareness module.

Knows each LLM's context window size and adjusts compression
intensity accordingly.
"""

from __future__ import annotations

MODEL_CONTEXT_WINDOWS: dict[str, int] = {
    "gpt-4": 128_000,
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "gpt-3.5-turbo": 16_385,
    "claude-3-opus": 200_000,
    "claude-3-sonnet": 200_000,
    "claude-3-haiku": 200_000,
    "claude-3.5-sonnet": 200_000,
    "gemini-1.5-pro": 1_000_000,
    "gemini-1.5-flash": 1_000_000,
}


class ContextWindowAnalyzer:
    def get_window_size(self, model: str) -> int:
        return MODEL_CONTEXT_WINDOWS.get(model, 128_000)

    def compute_urgency(self, model: str, current_tokens: int) -> str:
        """Returns compression urgency: minimal | balanced | aggressive."""
        window = self.get_window_size(model)
        ratio = current_tokens / window
        if ratio < 0.3:
            return "minimal"
        if ratio < 0.7:
            return "balanced"
        return "aggressive"
