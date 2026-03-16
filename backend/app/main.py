"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .api.middleware import PromptForgeMiddleware

app = FastAPI(
    title="PromptForge",
    description=(
        "한국어 감정·모호어 인식 기반 의도 보존형 프롬프트 재작성 필터. "
        "LLM 호출 전후 양방향 토큰 최적화 시스템."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PromptForgeMiddleware)

app.include_router(router)


@app.on_event("startup")
async def startup():
    # TODO: preload ML models, initialize DB connections
    pass
