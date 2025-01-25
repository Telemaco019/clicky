import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, logger: logging.Logger | None = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        self.logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "ip": request.client.host if request.client else "NA",
                "status_code": response.status_code,
            },
        )
        return response
