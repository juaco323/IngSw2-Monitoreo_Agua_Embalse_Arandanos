import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.log_context import ensure_correlation_id, set_correlation_id
from core.log_origins import LogLevel, LogOrigin
from core.log_service import log_service


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    HEADER = "X-Correlation-Id"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        cid = request.headers.get(self.HEADER) or ensure_correlation_id()
        set_correlation_id(cid)
        request.state.correlation_id = cid

        start = time.perf_counter()
        response = await call_next(request)
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        status = response.status_code

        if not request.url.path.startswith("/api/logs") and request.url.path not in ("/health",):
            level = LogLevel.INFO
            if status >= 500:
                level = LogLevel.FATAL
            elif status >= 400:
                level = LogLevel.WARN
            if status >= 400 or request.url.path.startswith("/api/"):
                log_service.log(
                    LogOrigin.DASHBOARD, level,
                    f"{request.method} {request.url.path} -> {status}",
                    component="api.http",
                    details={"path": request.url.path, "status_code": status, "duration_ms": elapsed},
                    correlation_id=cid,
                )
        response.headers[self.HEADER] = cid
        return response
