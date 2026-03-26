# 멀티모델 레지스트리 + 토큰 카운팅

**날짜**: 2026-03-27
**브랜치**: `feat/model-registry`
**관련 계획**: `phase_1_core_구현_a6f9a2ce.plan.md` → `model-registry`, `base-stage-tokens`

---

## 배경

기존 `tokenizer.py`는 tiktoken 단일 모델(gpt-4o-mini)만 지원했고,
`BaseStage.execute()`는 토큰 수를 전혀 기록하지 않았다.

---

## 변경 내용

### 1. 신규: `backend/app/utils/model_registry.py`

6개 프로바이더, 20개 모델의 메타데이터 레지스트리.

```python
@dataclass(frozen=True)
class ModelInfo:
    provider: str          # "openai" | "anthropic" | "google" | "meta" | "mistral" | "deepseek"
    model_id: str          # API 호출 ID
    display_name: str
    tokenizer_type: str    # "tiktoken" | "cl100k_approx" | "hf_approx"
    tokenizer_id: str      # tiktoken 인코딩명
    input_price_per_1k: float   # USD / 1K 입력 토큰
    output_price_per_1k: float  # USD / 1K 출력 토큰
    context_window: int
```

**등록 모델 목록:**

| 프로바이더 | 모델 | 토크나이저 전략 |
|-----------|------|----------------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo, o1, o3-mini | tiktoken (정확) |
| Anthropic | claude-3.5-sonnet, claude-3-haiku, claude-3-opus | cl100k_approx |
| Google | gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash | cl100k_approx |
| Meta | llama-3.1-70b, llama-3.1-8b | hf_approx |
| Mistral | mistral-large, mistral-small, mixtral-8x7b | hf_approx |
| DeepSeek | deepseek-chat(V3), deepseek-coder | tiktoken |

**공개 API:**
```python
get_model(model_id)              # → ModelInfo | None
get_model_or_default(model_id)   # → ModelInfo (없으면 gpt-4o-mini)
list_models(provider=None)       # → list[ModelInfo]
all_model_ids()                  # → list[str]
```

### 2. 확장: `backend/app/utils/tokenizer.py`

**신규 타입:**
```python
@dataclass
class ModelTokenResult:
    model_id: str
    input_tokens: int      # int — 토큰은 정수
    output_tokens: int     # int
    input_cost_usd: float  # float — 비용은 USD 소수
    output_cost_usd: float
    total_cost_usd: float  # property
```

**신규 함수:**
```python
count_tokens(text, model)                        # 단일 모델 토큰 수
count_cost(tokens, model_id, is_output)          # 토큰 → USD
count_tokens_with_cost(text, model_id, output)   # 입출력 합산
count_tokens_multi(text, model_ids, output)      # 여러 모델 한 번에
```

**토크나이저 분기:**
- `tiktoken`: 모델별 tiktoken 인코딩 직접 사용 (lru_cache)
- `cl100k_approx` / `hf_approx`: cl100k_base 근사 → Phase 2에서 AutoTokenizer로 교체

**int vs float 설계 원칙:**
- 토큰 수 → `int` (토큰은 정수 단위)
- 비용·비율 → `float` (USD, 절감 비율)

### 3. 수정: `backend/app/pipeline/context.py`

```python
compare_models: list[str]              # 비교 대상 모델 ID 목록
multi_model_tokens: dict[str, Any]     # {model_id: ModelTokenResult}
```

### 4. 수정: `backend/app/pipeline/base.py`

`execute()` 내부에서 `process()` 전후로 토큰 수 자동 기록:

```python
input_tokens  = _safe_count_tokens(snapshot,     ctx.target_model)
# ... process() 실행 ...
output_tokens = _safe_count_tokens(result.text,  ctx.target_model)

StageLog(input_tokens=input_tokens, output_tokens=output_tokens, ...)
```

`_safe_count_tokens()`: 토큰 카운팅 실패 시 0 반환 → 스테이지 실행 차단 없음.

---

## 다음 단계

- [ ] `nli-verifier` + `semantic-verifier` + `orchestrator-nli` 구현
- [ ] Orchestrator에서 `count_tokens_multi()` 호출 → `multi_model_tokens` 채우기
