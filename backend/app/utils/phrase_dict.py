"""Phrase→Word substitution dictionary for S7 (Phrase-to-Word Condenser)."""

from __future__ import annotations

# Korean phrase → shorter equivalent
KOREAN_PHRASE_MAP: dict[str, str] = {
    "사용하는 것이 가능한": "사용 가능한",
    "다시 한번 더": "다시",
    "그런 종류의": "그런",
    "하는 방법에 대해서": "방법",
    "가장 중요한 핵심적인": "핵심",
    "현재 시점에서": "현재",
    "그것에 대해서": "그것에 대해",
    "하는 것이 좋을 것 같습니다": "하세요",
    "하는 것이 가능한지 여부를 확인해주세요": "가능한지 확인해줘",
    "혹시 시간이 되신다면 한번 살펴봐 주실 수 있을까요": "살펴봐줘",
    "것을 할 수 있는": "할 수 있는",
    "에 관해서": "에 관해",
    "에 대해서": "에 대해",
    "이라고 하는": "인",
    "라고 불리는": "인",
    "하기 위해서는": "하려면",
    "하고 싶은데요": "하고 싶어",
    "해주시면 감사하겠습니다": "해줘",
    "해주실 수 있으신가요": "해줘",
}

# English phrase → shorter equivalent
ENGLISH_PHRASE_MAP: dict[str, str] = {
    "in order to": "to",
    "a large number of": "many",
    "at this point in time": "now",
    "due to the fact that": "because",
    "in the event that": "if",
    "for the purpose of": "to",
    "in spite of the fact that": "although",
    "in the near future": "soon",
    "on a daily basis": "daily",
    "at the present time": "currently",
    "with regard to": "regarding",
    "in addition to": "besides",
    "as a result of": "because of",
    "a number of": "several",
    "the majority of": "most",
}


def get_phrase_map(lang: str = "ko") -> dict[str, str]:
    if lang == "ko":
        return {**KOREAN_PHRASE_MAP, **ENGLISH_PHRASE_MAP}
    if lang == "en":
        return ENGLISH_PHRASE_MAP
    return {**KOREAN_PHRASE_MAP, **ENGLISH_PHRASE_MAP}
