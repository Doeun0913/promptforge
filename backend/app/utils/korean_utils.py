"""Korean-specific text processing utilities for S0.5."""

from __future__ import annotations

import re

# ── Honorific → plain conversion rules ───────────────────────────

HONORIFIC_ENDINGS: list[tuple[str, str]] = [
    (r"해주실 수 있으신가요\??", "해줘"),
    (r"해주실 수 있나요\??", "해줘"),
    (r"해주시겠어요\??", "해줘"),
    (r"해주세요", "해줘"),
    (r"하시겠습니까\??", "할래?"),
    (r"하십시오", "해"),
    (r"합니다", "해"),
    (r"합니까\??", "할래?"),
    (r"입니다", "이야"),
    (r"입니까\??", "이야?"),
    (r"습니다", "어"),
    (r"습니까\??", "어?"),
    (r"드리겠습니다", "줄게"),
    (r"드립니다", "줘"),
    (r"주시면 감사하겠습니다", "줘"),
    (r"부탁드립니다", "부탁해"),
]

# ── Verbose ending patterns ──────────────────────────────────────

VERBOSE_ENDINGS: list[tuple[str, str]] = [
    (r"하는 것이 좋을 것 같습니다", "하세요"),
    (r"하는 것이 좋겠습니다", "하세요"),
    (r"인 것 같습니다", "인 것 같아"),
    (r"것 같은데요", "것 같아"),
    (r"라고 생각합니다", "라고 생각해"),
]


def normalize_honorifics(text: str) -> str:
    """Convert formal/honorific endings to plain speech."""
    for pattern, replacement in HONORIFIC_ENDINGS:
        text = re.sub(pattern, replacement, text)
    return text


def compress_endings(text: str) -> str:
    """Compress verbose Korean sentence endings."""
    for pattern, replacement in VERBOSE_ENDINGS:
        text = re.sub(pattern, replacement, text)
    return text


def normalize_particles(text: str) -> str:
    """Optimize redundant particle usage."""
    # TODO: implement particle optimization (것을→걸, 것이→게, etc.)
    return text


def fix_spacing(text: str) -> str:
    """Basic spacing correction."""
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def korean_preprocess(text: str) -> str:
    """Full Korean preprocessing pipeline."""
    text = normalize_honorifics(text)
    text = compress_endings(text)
    text = normalize_particles(text)
    text = fix_spacing(text)
    return text
