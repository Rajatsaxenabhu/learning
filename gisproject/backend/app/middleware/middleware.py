import time
import uuid

from fastapi import FastAPI
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.conf.logging.applog import logger
from app.conf.logging.context import request_id_var

_REQUEST_ID_HEADER = b"x-request-id"
_UNLOGGED_PATHS = {"/docs", "/redoc", "/openapi.json"}


class LoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        incoming_id = next(
            (v.decode() for k, v in scope.get("headers", []) if k == _REQUEST_ID_HEADER),
            None,
        )
        request_id = incoming_id or uuid.uuid4().hex
        token = request_id_var.set(request_id)

        start = time.perf_counter()
        client = scope.get("client")
        client_host = client[0] if client else "-"
        path = scope.get("path", "-")
        status = "-"

        async def send_wrapper(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message.setdefault("headers", []).append(
                    (_REQUEST_ID_HEADER, request_id.encode())
                )
            elif message["type"] == "websocket.accept":
                status = "accepted"
            elif message["type"] == "websocket.close":
                status = message.get("code", "closed")
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            method = "WS" if scope["type"] == "websocket" else scope.get("method", "-")
            if path not in _UNLOGGED_PATHS:
                logger.info(
                    f'{client_host} - "{method} {path}" {status} {duration_ms:.1f}ms',
                    extra={
                        "method": method,
                        "path": path,
                        "status_code": status,
                        "duration_ms": round(duration_ms, 1),
                        "client": client_host,
                    },
                )
            request_id_var.reset(token)


def setup_logging_middleware(app: FastAPI) -> None:
    app.add_middleware(LoggingMiddleware)
