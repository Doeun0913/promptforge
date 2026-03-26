"""Dynamic Korean slang / emotion expression updater.

나무위키·국립국어원에서 한국어 신조어·유행어·긍정/부정 표현을 자동 수집하여
정적 패턴 목록(patterns.py)을 보완한다.

Why this exists
---------------
``patterns.py``의 정적 목록은 빠르게 낡는다. 예:

    부정: "샤갈"(2024~) "현타"(2019~) "킹받아"(2021~) "존버"(2017~)
    긍정: "갓"(2010s~) "레전드"(2010s~) "꿀잼"(2015~) "혜자"(2015~)
            "찰떡"(2020~) "역대급"(2018~) "핵이득"(2016~)

AI 모델(KcBERT)이 서브워드 토크나이징+문맥으로 미등록 신조어를 처리하지만,
규칙 기반 폴백 레이어가 명시적 패턴 목록을 필요로 한다.

크롤링 소스
-----------
부정/일반:
    - 나무위키 분류:유행어 / 분류:신조어 / 분류:인터넷 은어 / 분류:비속어
    - 국립국어원 우리말샘 신조어·비속어 API

긍정:
    - 나무위키 분류:칭찬하는 말 / 분류:감탄사 / 분류:인터넷 밈
    - 국립국어원 우리말샘 긍정 표현 API
    - 전용 긍정 시드 키워드 기반 분류

캐시
----
``backend/data/korean_slang_cache.json`` (TTL: ``SLANG_CACHE_TTL_HOURS``, 기본 24h)
"""

from __future__ import annotations

import json
import logging
import os
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ── 경로 / 설정 ───────────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_CACHE_FILE = _DATA_DIR / "korean_slang_cache.json"
_CACHE_TTL_HOURS: int = int(os.getenv("SLANG_CACHE_TTL_HOURS", "24"))

# ── 크롤링 엔드포인트 ─────────────────────────────────────────────────────

_NAMU_API_BASE = "https://namu.wiki/api"

# 부정/중립 신조어 카테고리
_NAMU_CATEGORIES_GENERAL = [
    "분류:유행어",
    "분류:신조어",
    "분류:인터넷 은어",
    "분류:비속어",
]

# 긍정 표현 특화 카테고리
_NAMU_CATEGORIES_POSITIVE = [
    "분류:칭찬하는 말",
    "분류:감탄사",
    "분류:인터넷 밈",       # 밈 중 긍정적 표현 포함
    "분류:한국어 감탄사",
]

_KOREAN_DICT_API_URL = "https://opendict.korean.go.kr/api/search"

# 부정 검색어
_KOREAN_DICT_TERMS_NEGATIVE = ["신조어", "비속어", "유행어", "인터넷용어"]
# 긍정 검색어
_KOREAN_DICT_TERMS_POSITIVE = ["감탄사", "칭찬", "긍정표현", "기쁨표현"]

# ── 감정 분류 시드 키워드 ─────────────────────────────────────────────────
# _heuristic_classify() 에서 사용. Phase 2에서 AI zero-shot 분류로 교체 예정.

_NEG_SEED_KEYWORDS = [
    "욕설", "비속어", "짜증", "불만", "혐오", "분노", "슬픔", "실망",
    "황당", "어이없", "답답", "열받", "화남", "분함", "킹받", "극혐",
    "현타", "멘붕", "빡침", "빡쳐", "뚜껑", "갈굼", "꼴보기", "역겨",
    "한심", "짜증", "화딱지", "기가막", "어처구니",
]

_POS_SEED_KEYWORDS = [
    # 인터넷 긍정 슬랭
    "갓", "레전드", "꿀잼", "존잼", "개이득", "핵이득", "혜자", "찰떡",
    "역대급", "신박", "개쩔", "존쩔", "대박", "띵작", "명작", "갓성비",
    "실화냐", "개굿", "개좋", "존좋", "킹", "황송", "영광", "감격",
    # 감정/칭찬 표현
    "감탄", "기쁨", "행복", "최고", "칭찬", "감사", "훌륭", "완벽",
    "뿌듯", "설레", "두근", "흥분", "즐거", "재밌", "웃기", "귀엽",
    "사랑스럽", "멋지", "예쁘", "아름다", "놀라", "신기", "신나",
    # 만족/성공
    "성공", "해결", "드디어", "결국", "마침내", "완료", "해냈",
]


# ── 캐시 ─────────────────────────────────────────────────────────────────


class SlangCache:
    """JSON 기반 로컬 캐시 (파일 단위)."""

    def __init__(self, path: Path = _CACHE_FILE) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any] | None:
        if not self._path.exists():
            return None
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("슬랭 캐시 로드 실패: %s", exc)
            return None

    def is_fresh(self) -> bool:
        cached = self.load()
        if not cached or "updated_at" not in cached:
            return False
        updated_at = datetime.fromisoformat(cached["updated_at"])
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        return datetime.now(tz=timezone.utc) - updated_at < timedelta(hours=_CACHE_TTL_HOURS)

    def save(self, data: dict[str, Any]) -> None:
        data["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("슬랭 캐시 저장: %s", self._path)


# ── 크롤러 ────────────────────────────────────────────────────────────────


class KoreanSlangUpdater:
    """한국어 신조어·유행어·긍정/부정 표현을 온라인 소스에서 자동 수집한다.

    부정뿐 아니라 긍정 표현도 전용 소스(분류:칭찬하는 말, 분류:감탄사 등)에서
    별도로 크롤링하여 정적 목록을 대체한다.

    Example::

        updater = KoreanSlangUpdater()
        patterns = await updater.get_patterns()
        # patterns["negative"]     → ["샤갈", "현타", "킹받아", ...]
        # patterns["positive"]     → ["갓", "레전드", "꿀잼", "찰떡", ...]
        # patterns["neutral_slang"] → [...]
    """

    def __init__(
        self,
        cache: SlangCache | None = None,
        api_key: str | None = None,
    ) -> None:
        self._cache = cache or SlangCache()
        self._api_key = api_key or os.getenv("KOREAN_DICT_API_KEY")

    # ── 공개 API ─────────────────────────────────────────────────────────

    async def get_patterns(self, force_refresh: bool = False) -> dict[str, list[str]]:
        """패턴 딕셔너리 반환.

        캐시가 신선하면 캐시 사용, 만료 또는 force_refresh이면 크롤링 후 저장.

        Returns:
            dict with keys: ``negative``, ``positive``, ``neutral_slang``
        """
        if not force_refresh and self._cache.is_fresh():
            cached = self._cache.load()
            if cached:
                logger.debug("슬랭 캐시 히트")
                return {
                    "negative": cached.get("negative", []),
                    "positive": cached.get("positive", []),
                    "neutral_slang": cached.get("neutral_slang", []),
                }

        logger.info("슬랭 패턴 크롤링 시작")
        patterns = await self._crawl_all()
        self._cache.save(patterns)
        return patterns

    def get_patterns_sync(self) -> dict[str, list[str]]:
        """동기 편의 메서드 — 캐시에서만 읽는다.

        서버 시작 시 빠른 초기화에 사용. 캐시 없으면 빈 딕셔너리 반환.
        """
        cached = self._cache.load()
        if cached:
            return {
                "negative": cached.get("negative", []),
                "positive": cached.get("positive", []),
                "neutral_slang": cached.get("neutral_slang", []),
            }
        return {"negative": [], "positive": [], "neutral_slang": []}

    # ── 크롤링 ───────────────────────────────────────────────────────────

    async def _crawl_all(self) -> dict[str, list[str]]:
        negative: list[str] = []
        positive: list[str] = []
        neutral: list[str] = []

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=True,
            headers={"User-Agent": "PromptForge/1.0 (research; contact@promptforge.dev)"},
        ) as client:
            # ── 나무위키: 부정/일반 카테고리 ──────────────────────────────
            for cat in _NAMU_CATEGORIES_GENERAL:
                for word in await self._fetch_namu_category(client, cat):
                    label = self._heuristic_classify(word)
                    if label == "negative":
                        negative.append(word)
                    elif label == "positive":
                        positive.append(word)
                    else:
                        neutral.append(word)

            # ── 나무위키: 긍정 전용 카테고리 ─────────────────────────────
            # 긍정 소스에서 수집된 단어는 기본 positive로 분류
            # (명백히 부정인 경우만 재분류)
            for cat in _NAMU_CATEGORIES_POSITIVE:
                for word in await self._fetch_namu_category(client, cat):
                    label = self._heuristic_classify(word)
                    if label == "negative":
                        negative.append(word)   # 긍정 카테고리에서도 간혹 부정 단어 등장
                    else:
                        positive.append(word)   # 긍정 소스 → positive 우선

            # ── 국립국어원 API ─────────────────────────────────────────
            if self._api_key:
                neg_words = await self._fetch_korean_dict(
                    client, _KOREAN_DICT_TERMS_NEGATIVE
                )
                pos_words = await self._fetch_korean_dict(
                    client, _KOREAN_DICT_TERMS_POSITIVE
                )
                for word in neg_words:
                    if self._heuristic_classify(word) != "positive":
                        negative.append(word)
                for word in pos_words:
                    positive.append(word)
            else:
                logger.debug("KOREAN_DICT_API_KEY 미설정 — 국립국어원 API 스킵")

        # 중복 제거
        negative = list(set(negative))
        positive = list(set(positive))
        neutral = list(set(neutral))

        logger.info(
            "슬랭 크롤링 완료: neg=%d pos=%d neutral=%d",
            len(negative), len(positive), len(neutral),
        )
        return {"negative": negative, "positive": positive, "neutral_slang": neutral}

    async def _fetch_namu_category(
        self,
        client: httpx.AsyncClient,
        category: str,
    ) -> list[str]:
        """나무위키 분류 페이지에서 표제어 목록 수집.

        나무위키 비공식 REST API: ``/api/category/{encoded}/list``
        응답 형식: ``{"result": [{"title": "표제어"}, ...]}``
        """
        try:
            encoded = urllib.parse.quote(category, safe="")
            url = f"{_NAMU_API_BASE}/category/{encoded}/list"
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.debug("나무위키 %s → HTTP %d", category, resp.status_code)
                return []
            data = resp.json()
            items = data.get("result", [])
            words = [item["title"] for item in items if "title" in item]
            logger.debug("나무위키 %s: %d개 수집", category, len(words))
            return words
        except Exception as exc:
            logger.debug("나무위키 크롤링 실패 (%s): %s", category, exc)
            return []

    async def _fetch_korean_dict(
        self,
        client: httpx.AsyncClient,
        search_terms: list[str],
    ) -> list[str]:
        """국립국어원 우리말샘 OpenAPI.

        API 문서: https://opendict.korean.go.kr/service/openDicPortal
        """
        words: list[str] = []
        for term in search_terms:
            try:
                params = {
                    "key": self._api_key,
                    "q": term,
                    "part": "word",
                    "sort": "popular",
                    "num": "50",
                    "type1": "new",
                }
                resp = await client.get(_KOREAN_DICT_API_URL, params=params)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                items = data.get("channel", {}).get("item", [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict) and "word" in item:
                            words.append(item["word"])
            except Exception as exc:
                logger.debug("국립국어원 API 실패 (%s): %s", term, exc)
        unique = list(set(words))
        logger.debug("국립국어원 API (%s): %d개", search_terms, len(unique))
        return unique

    # ── 휴리스틱 분류 ────────────────────────────────────────────────────

    @staticmethod
    def _heuristic_classify(word: str) -> str:
        """단어를 시드 키워드로 긍정/부정/중립 분류.

        Phase 2에서 KcBERT zero-shot 분류로 교체 예정.

        Returns:
            ``"negative"`` | ``"positive"`` | ``"neutral"``
        """
        for kw in _NEG_SEED_KEYWORDS:
            if kw in word:
                return "negative"
        for kw in _POS_SEED_KEYWORDS:
            if kw in word:
                return "positive"
        return "neutral"


# ── 싱글턴 / 편의 함수 ────────────────────────────────────────────────────

_updater: KoreanSlangUpdater | None = None


def get_updater() -> KoreanSlangUpdater:
    """애플리케이션 전역 싱글턴 updater 반환."""
    global _updater
    if _updater is None:
        _updater = KoreanSlangUpdater()
    return _updater


def get_cached_negative_patterns() -> list[str]:
    """동기 편의 함수 — 캐시된 부정 패턴 목록 반환."""
    return get_updater().get_patterns_sync().get("negative", [])


def get_cached_positive_patterns() -> list[str]:
    """동기 편의 함수 — 캐시된 긍정 패턴 목록 반환."""
    return get_updater().get_patterns_sync().get("positive", [])
