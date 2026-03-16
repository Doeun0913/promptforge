"""Tests for Korean preprocessing utilities."""

from app.utils.korean_utils import (
    normalize_honorifics,
    compress_endings,
    fix_spacing,
    korean_preprocess,
)


def test_honorific_normalization():
    assert normalize_honorifics("해주세요") == "해줘"
    assert normalize_honorifics("부탁드립니다") == "부탁해"


def test_verbose_ending_compression():
    text = "하는 것이 좋을 것 같습니다"
    assert compress_endings(text) == "하세요"


def test_fix_spacing():
    assert fix_spacing("  hello   world  ") == "hello world"


def test_full_preprocess():
    text = "해주시면 감사하겠습니다"
    result = korean_preprocess(text)
    assert result == "해줘"
