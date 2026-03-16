"""LLM proxy middleware – intercepts requests for transparent filtering."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class PromptForgeMiddleware(BaseHTTPMiddleware):
    """
    Middleware that can intercept /v1/chat/completions requests,
    apply the filter pipeline, and forward to the real LLM.
    Currently a placeholder for Phase 5 implementation.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # TODO: Phase 5 – intercept, filter, proxy, post-filter
        return await call_next(request)
