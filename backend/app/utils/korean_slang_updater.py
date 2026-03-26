"""Dynamic Korean slang / emotion expression updater.

나무위키·국립국어원에서 한국어 신조어·유행어·비속어를 자동 수집하여
정적 패턴 목록(patterns.py)을 보완한다.

Why this exists
---------------
``patterns.py``의 정적 목록은 빠르게 낡는다. 새로운 표현 예시:

    - "샤갈"   (2024~) : 황당·어이없음 감탄사
    - "현타"   (2019~) : 현실 자각 타임 → 무기력·실망 감정
    - "킹받아" (2021~) : 극도로 짜증남
    - "존버"   (2017~) : 인내·버팀 (감정 맥락에 따라 부정적)

AI 모델(KcBERT, KLUE-BERT)이 서브워드 토크나이징과 문맥 어텐션으로
미등록 신조어를 처리하지만, 명시적 패턴 목록은 규칙 기반 폴백 레이어를 지원한다.

크롤링 소스 (우선순위 순)
--------------------------
1. 국립국어원 우리말샘 OpenAPI — env ``KOREAN_DICT_API_KEY`` 필요
2. 나무위키 분류:유행어 / 분류:신조어 카테고리 API
3. 캐시된 JSON 스냅샷 (TTL: ``SLANG_CACHE_TTL_HOURS``, 기본 24시간)

캐시 파일
---------
``backend/data/korean_slang_cache.json``
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
_NAMU_CATEGORIES = ["분류:유행어", "분류:신조어", "분류:인터넷 은어"]

_KOREAN_DICT_API_URL = "https://opendict.korean.go.kr/api/search"
_KOREAN_DICT_SEARCH_TERMS = ["신조어", "비속어", "유행어", "인터넷용어"]

# ── 감정 분류 시드 키워드 (휴리스틱 fallback) ─────────────────────────────
# Phase 2에서 AI 분류로 교체됨

_NEG_SEED_KEYWORDS = [
    "욕설", "비속어", "짜증", "불만", "혐오", "분노", "슬픔", "실망",
    "황당", "어이없", "답답", "열받", "화남", "분함", "킹받", "극혐",
    "현타", "멘붕", "빡침", "빡쳐", "뚜껑", "갈굼",
]
_POS_SEED_KEYWORDS = [
    "감탄", "기쁨", "행복", "좋아", "최고", "칭찬", "감사", "대박",
    "레전드", "갓", "신박", "핵심", "개이득",
]


# ── 캐시 ─────────────────────────────────────────────────────────────────


class SlangCache:
    """JSON 기반 로컬 캐시 (파일 단위)."""

    def __init__(self, path: Path = _CACHE_FILE) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    # -- read ---

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

    # -- write --

    def save(self, data: dict[str, Any]) -> None:
        data["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("슬랭 캐시 저장: %s", self._path)


# ── 크롤러 ────────────────────────────────────────────────────────────────


class KoreanSlangUpdater:
    """한국어 신조어·유행어·비속어를 온라인 소스에서 자동 수집한다.

    Example::

        updater = KoreanSlangUpdater()
        patterns = await updater.get_patterns()
        # patterns["negative"] → ["샤갈", "현타", "킹받아", ...]
        # patterns["positive"] → ["레전드", "갓", ...]
        # patterns["neutral_slang"] → [...]

    캐시가 신선하면 네트워크 요청 없이 캐시를 반환한다.
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

        캐시가 신선하면 캐시 사용, 만료되었거나 force_refresh이면 크롤링.

        Returns:
            dict with keys ``negative``, ``positive``, ``neutral_slang``
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
            # 1) 나무위키 카테고리
            namu_words: list[str] = []
            for cat in _NAMU_CATEGORIES:
                words = await self._fetch_namu_category(client, cat)
                namu_words.extend(words)

            # 2) 국립국어원 우리말샘 (API 키 있을 때만)
            dict_words: list[str] = []
            if self._api_key:
                dict_words = await self._fetch_korean_dict(client)
            else:
                logger.debug("KOREAN_DICT_API_KEY 미설정 — 국립국어원 API 스킵")

            combined = list(set(namu_words + dict_words))

            # 3) 휴리스틱 분류 (Phase 2: AI 분류로 교체 예정)
            for word in combined:
                label = self._heuristic_classify(word)
                if label == "negative":
                    negative.append(word)
                elif label == "positive":
                    positive.append(word)
                else:
                    neutral.append(word)

        logger.info(
            "슬랭 크롤링 완료: neg=%d pos=%d neutral=%d (후보 %d개)",
            len(negative), len(positive), len(neutral), len(combined),
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

    async def _fetch_korean_dict(self, client: httpx.AsyncClient) -> list[str]:
        """국립국어원 우리말샘 OpenAPI.

        API 문서: https://opendict.korean.go.kr/service/openDicPortal
        결과에서 word 필드만 추출.
        """
        words: list[str] = []
        for term in _KOREAN_DICT_SEARCH_TERMS:
            try:
                params = {
                    "key": self._api_key,
                    "q": term,
                    "part": "word",
                    "sort": "popular",
                    "num": "50",
                    "type1": "new",  # 신어 필터
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
        logger.debug("국립국어원 API: %d개 수집", len(unique))
        return unique

    # ── 휴리스틱 분류 ────────────────────────────────────────────────────

    @staticmethod
    def _heuristic_classify(word: str) -> str:
        """단어를 간단한 시드 키워드로 분류한다.

        Phase 2에서 AI 분류 (KcBERT zero-shot)로 교체될 임시 구현.

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
    """동기 편의 함수 — 캐시된 부정 패턴 목록 반환.

    캐시 없으면 빈 리스트 반환 (크롤링 수행 안 함).
    patterns.py의 ``get_all_negative_patterns()``에서 호출됨.
    """
    return get_updater().get_patterns_sync().get("negative", [])


def get_cached_positive_patterns() -> list[str]:
    """동기 편의 함수 — 캐시된 긍정 패턴 목록 반환."""
    return get_updater().get_patterns_sync().get("positive", [])
