# 감정 감지 AI화 + 동적 슬랭 크롤러

**날짜**: 2026-03-26
**브랜치**: `feat/emotion-ai-detector`
**관련 계획**: `phase_1_core_구현_a6f9a2ce.plan.md` → `emotion-layer` 항목

---

## 배경

`patterns.py`의 정적 패턴 목록은 새로운 한국어 유행어·신조어에 빠르게 낡는다.

예:
- `"샤갈"` (2024~): 황당·어이없음 감탄사
- `"현타"` (2019~): 현실 자각 타임 → 무기력·실망
- `"킹받아"` (2021~): 극도로 짜증남

이를 해결하기 위해 **두 가지 접근**을 병행 도입했다.

---

## 변경 내용

### 1. 새 파일: `backend/app/utils/korean_slang_updater.py`

**한국어 신조어·유행어 동적 크롤러**.

| 항목 | 내용 |
|------|------|
| 크롤링 소스 | 나무위키 `분류:유행어` / `분류:신조어` / `분류:인터넷 은어` |
| 크롤링 소스 | 국립국어원 우리말샘 OpenAPI (`KOREAN_DICT_API_KEY` env 필요) |
| 캐시 | `backend/data/korean_slang_cache.json` (TTL: 24시간, `SLANG_CACHE_TTL_HOURS` env 조정 가능) |
| 분류 | 현재 휴리스틱 키워드 분류 → Phase 2에서 AI zero-shot 분류로 교체 예정 |
| 편의 함수 | `get_cached_negative_patterns()`, `get_cached_positive_patterns()` |

### 2. `backend/app/utils/patterns.py` 수정

파일 말미에 동적 로딩 함수 추가:

```python
def get_all_negative_patterns() -> list[str]:
    """정적 패턴 + 동적 크롤링 패턴의 합집합"""

def get_all_positive_patterns() -> list[str]:
    """정적 패턴 + 동적 크롤링 패턴의 합집합"""
```

기존 `NEGATIVE_EMOTION_INTERJECTIONS` 등 정적 상수는 그대로 유지되며
크롤링 캐시 없어도 항상 안전하게 폴백된다.

### 3. `backend/app/models/emotion_classifier.py` 전면 개선

**AI 기반 감정 분류 실제 구현** (Phase 1.5):

| 항목 | 내용 |
|------|------|
| 기본 모델 | `snunlp/KR-FinBert-SC` (한국어 3-class 감정 분류) |
| 라벨 정규화 | 한국어/영어/LABEL_N/별점 등 다양한 모델 출력 자동 매핑 |
| 폴백 | 모델 로드 실패 시 `_rule_based_predict()` 자동 전환 |
| Phase 2 stub | `predict_ensemble()` — KcBERT(0.6) + KLUE-BERT(0.4) 앙상블 자리 |

**AI 감지가 신조어를 처리하는 원리**:
- 서브워드 토크나이징: `"샤갈"` → `["샤", "##갈"]` 형태소로 분해
- 문맥 어텐션: 부정적 문맥 속 중립 단어도 NEGATIVE로 분류
- 학습 데이터: KcBERT는 한국 SNS·커뮤니티 텍스트로 사전학습됨

### 4. `backend/app/pipeline/stage1_emotion.py` 전면 개선

**실제 감정 분류·표현 추출 로직 연결**:

- `EmotionClassifierModel.predict()` 호출
- `_extract_expressions()`: patterns + 정규식으로 감정 표현 span 추출
- `_determine_reanalysis()`: frustration_streak ≥ 2 또는 이전 턴 감정 변화 시 `requires_reanalysis=True`
- `EmotionSnapshot` 생성 및 `emotion_history` 누적
- `StageResult.metadata`에 디버깅 정보 포함

### 5. `backend/requirements.txt` 수정

`beautifulsoup4>=4.12.0` 추가 (크롤러용 HTML 파싱 보조).

### 6. `.gitignore` 수정

`backend/data/korean_slang_cache.json` 제외 (런타임 생성 파일).

---

## 아키텍처

```
사용자 입력
    │
    ▼
[Stage 1: EmotionSeparatorStage]
    │
    ├─→ EmotionClassifierModel.predict(text)
    │       ├─ AI 모델 (snunlp/KR-FinBert-SC)  ← 신조어 자동 처리
    │       └─ 폴백: _rule_based_predict()
    │                   └─ get_all_negative_patterns()
    │                           ├─ NEGATIVE_EMOTION_INTERJECTIONS (정적)
    │                           └─ get_cached_negative_patterns()  (동적)
    │                                   └─ korean_slang_cache.json
    │                                           ↑ (24h TTL)
    │                                   KoreanSlangUpdater.get_patterns()
    │                                           ├─ 나무위키 분류:유행어
    │                                           └─ 국립국어원 우리말샘 API
    │
    ├─→ _extract_expressions(text) → expressions
    ├─→ _determine_reanalysis()    → requires_reanalysis, reanalysis_reason
    └─→ EmotionLayer 업데이트
```

---

## 향후 계획 (Phase 2)

- [ ] `_heuristic_classify()` → KcBERT zero-shot 분류로 교체
- [ ] `predict_ensemble()` 실제 구현 (KcBERT 0.6 + KLUE-BERT 0.4)
- [ ] intent_text에서 expressions 정확한 span 제거
- [ ] 크롤러 스케줄러 연동 (`main.py` background task)
- [ ] GPU device auto-detection
