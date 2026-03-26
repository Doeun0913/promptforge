# [설계 보류] 역접/전환 감정 처리 (Adversative Handling)

**상태**: 설계 완료, 구현 보류 (model-registry / base-stage-tokens 이후 진행)
**관련 스테이지**: Stage 1 (EmotionSeparatorStage)

---

## 문제

현재 시스템은 문장을 통째로 분류 → 역접 이후 감정이 무시됨.

```
"완전 좋은데 근데 왜 이렇게 안 되지?"
 ↑ 긍정 히트          ↑ 부정 히트
→ 단순 합산 → 감정 희석
```

한국어 SOV 구조상 감정의 "결론"은 문장 끝에 위치 → **후반부가 진짜 감정**.

---

## 뒤집히는 패턴 3종류

| 종류 | 예시 | 진짜 감정 |
|------|------|----------|
| 역접 접속사 | "좋은데 **근데** 왜 안 돼?" | NEGATIVE |
| 양보 + 말줄임표 | "이해는 했는데**…**" | NEGATIVE |
| 부정 범위 | "**안** 좋아", "좋지 **않아**" | NEGATIVE |

---

## 설계

### 추가할 패턴 (patterns.py)

```python
# 역접/전환 마커
ADVERSATIVE_MARKERS: list[str] = [
    "근데", "그런데", "하지만", "그렇지만", "그래도", "그러나",
    "반면에", "오히려", "그럼에도", "근데도", "그러나",
]

# 양보 표현 (앞절 긍정 + 뒷절 불만)
CONCESSIVE_PATTERNS: list[str] = [
    r"\S+긴\s*(한|하)데",     # "좋긴 한데", "맞긴 하데"
    r"\S+기는\s*(해|하)도",   # "알기는 해도"
    r"\S+긴\s*(했|하)지만",   # "좋긴 했지만"
]

# 부정 범위 마커
NEGATION_MARKERS: list[str] = [
    "안", "못", "않", "아니", "없", "별로", "그다지", "딱히", "전혀",
]
```

### 핵심 알고리즘 (stage1_emotion.py)

```python
def analyze_with_adversative(text, classifier):
    clauses = split_by_adversative(text)   # 역접 마커로 절 분리

    if len(clauses) == 1:
        # 단순 문장 → 부정 범위만 처리 후 분류
        return apply_negation_scope(classifier.predict(text), text)

    scores = [classifier.predict(c) for c in clauses]

    # 마지막 절 가중치 (한국어 SOV 특성)
    # 절 2개: [0.3, 0.7] / 3개: [0.2, 0.3, 0.5] / 4개+: 마지막 0.4, 나머지 균등
    weights = _clause_weights(len(clauses))
    final_score = sum(s.sentiment_score * w for s, w in zip(scores, weights))

    return weighted_result(final_score, clauses, scores)

def apply_negation_scope(prediction, text):
    """부정 마커(안/못/않/아니) 범위 내 감정어 반전."""
    # 예: "안 좋아" → 긍정 히트를 부정으로 반전
    ...
```

### 양보 + 말줄임표 특수 처리

```python
# "좋긴 한데...", "괜찮긴 해요..." → NEGATIVE (passive-aggressive)
TRAILING_CONCESSIVE = r"(\S+긴\s*(한|하)(데|지만))\s*[.…]{2,}$"
```

---

## 구현 시 변경 파일

| 파일 | 변경 내용 |
|------|----------|
| `patterns.py` | ADVERSATIVE_MARKERS, CONCESSIVE_PATTERNS, NEGATION_MARKERS 추가 |
| `stage1_emotion.py` | `_split_clauses()`, `_apply_negation_scope()`, `_clause_weights()` 추가 |
| `emotion_classifier.py` | 절 단위 분류 + 가중 합산 로직 |

---

## 우선순위

model-registry → base-stage-tokens → nli-verifier → **이 기능** 순서로 진행 예정.
