import json
import logging
import time
import uuid
from contextvars import ContextVar

from fastapi import Request, Response
from prometheus_client import Counter, Histogram

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="unknown")
REQUESTS = Counter("platform_http_requests_total", "HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("platform_http_request_duration_seconds", "HTTP latency", ["path"])
LLM_CALLS = Counter("platform_llm_calls_total", "LLM calls", ["provider", "outcome"])
LLM_COST = Counter("platform_llm_estimated_cost_usd_total", "Estimated LLM cost", ["provider"])


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "level": record.levelname,
                "message": record.getMessage(),
                "request_id": request_id_ctx.get(),
                "timestamp": time.time(),
            }
        )


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("climate-ai")
logger.handlers = [handler]
logger.setLevel(logging.INFO)


async def telemetry_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    token = request_id_ctx.set(request_id)
    started = time.perf_counter()
    try:
        response = await call_next(request)
        return response
    finally:
        status = getattr(locals().get("response"), "status_code", 500)
        elapsed = time.perf_counter() - started
        REQUESTS.labels(request.method, request.url.path, status).inc()
        LATENCY.labels(request.url.path).observe(elapsed)
        logger.info(
            "request_complete method=%s path=%s status=%s latency_ms=%.1f",
            request.method,
            request.url.path,
            status,
            elapsed * 1000,
        )
        request_id_ctx.reset(token)
