# 긍정 감정 표현 동적화

**날짜**: 2026-03-27
**브랜치**: `feat/emotion-ai-detector`
**이전 작업**: `2026-03-26-emotion-ai-detector.md`

---

## 배경

이전 작업에서 부정 표현은 나무위키 크롤링으로 동적화됐지만,
긍정 표현은 정적 목록(`POSITIVE_EMOTION_EXPRESSIONS`)에만 의존하고 있었다.

"갓", "레전드", "꿀잼", "찰떡", "역대급", "혜자" 같은 인터넷 긍정 슬랭이
업데이트되지 않는 문제 → 긍정도 동적 크롤링 체계로 전환.

---

## 변경 내용

### `backend/app/utils/korean_slang_updater.py`

#### 긍정 전용 나무위키 카테고리 추가

```python
_NAMU_CATEGORIES_POSITIVE = [
    "분류:칭찬하는 말",
    "분류:감탄사",
    "분류:인터넷 밈",       # 긍정적 밈 포함
    "분류:한국어 감탄사",
]
```

#### 국립국어원 긍정 검색어 추가

```python
_KOREAN_DICT_TERMS_POSITIVE = ["감탄사", "칭찬", "긍정표현", "기쁨표현"]
```

#### `_POS_SEED_KEYWORDS` 대폭 확장

인터넷 긍정 슬랭 시드 추가:
`갓`, `레전드`, `꿀잼`, `존잼`, `개이득`, `핵이득`, `혜자`, `찰떡`, `역대급`, `신박`,
`개쩔`, `존쩔`, `대박`, `띵작`, `명작`, `갓성비`, `실화냐`, `개굿`, `개좋`, `존좋`, `킹` 등

#### 긍정 소스 우선 분류 로직

긍정 전용 카테고리에서 수집된 단어는 기본값을 `positive`로 설정.
명백히 부정인 경우에만 `negative`로 재분류.

```python
for cat in _NAMU_CATEGORIES_POSITIVE:
    for word in await self._fetch_namu_category(client, cat):
        label = self._heuristic_classify(word)
        if label == "negative":
            negative.append(word)
        else:
            positive.append(word)  # 긍정 소스 → positive 우선
```

### `backend/app/utils/patterns.py`

#### `POSITIVE_EMOTION_EXPRESSIONS` 역할 명확화

주석으로 "정적 앵커 (격식체·범용 표현)" 명시.
인터넷 슬랭은 `get_all_positive_patterns()`의 동적 레이어에서 담당.

#### `POSITIVE_EMOTION_JAMO_PATTERNS` 대폭 확장

| 추가 패턴 | 설명 |
|-----------|------|
| `ㅋ{2,}` | ㅋㅋ도 긍정 (기존 3개 이상 → 2개 이상으로 완화) |
| `하하하 이상` | 웃음 음절 반복 강화 |
| `호호호`, `헤헤헤` | 다양한 웃음 형태 추가 |
| `와아아`, `오오오!` | 감탄 음절 반복 |
| `:)`, `:D`, `><` | ASCII 이모티콘 추가 |
| `!!` 이상 | 느낌표 연속 (긍정 강조) |
| `진짜/완전/너무 + 좋/대박/최고` | 강조 부사 + 긍정어 조합 정규식 |

---

## 아키텍처 (업데이트)

```
KoreanSlangUpdater._crawl_all()
    │
    ├─ _NAMU_CATEGORIES_GENERAL  → 부정/중립 신조어
    │   유행어 / 신조어 / 인터넷 은어 / 비속어
    │
    ├─ _NAMU_CATEGORIES_POSITIVE → 긍정 표현 전용  ← 신규
    │   칭찬하는 말 / 감탄사 / 인터넷 밈 / 한국어 감탄사
    │
    └─ 국립국어원 API
        ├─ 부정 검색: 신조어 / 비속어 / 유행어
        └─ 긍정 검색: 감탄사 / 칭찬 / 긍정표현  ← 신규
```

---

## 향후 계획 (Phase 2)

- [ ] `_heuristic_classify()` → KcBERT zero-shot 분류로 교체
      (시드 키워드 의존 없이 단어 자체를 AI가 감정 분류)
- [ ] 긍정 강도(intensity) 세분화: MILD / MODERATE / STRONG
- [ ] 이모지 (`😊`, `🔥`, `👍`) 패턴 지원
