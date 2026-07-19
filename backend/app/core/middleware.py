import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import get_logger

logger = get_logger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        request_id = request.headers.get("x-request-id", "N/A")
        start_time = time.time()

        # Log incoming request
        logger.info(
            f"REQUEST | {request.method} | {request.url.path} | "
            f"Query: {dict(request.query_params) if request.query_params else 'None'} | "
            f"Request ID: {request_id}"
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log response
            logger.info(
                f"RESPONSE | {request.method} | {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Time: {process_time:.3f}s | "
                f"Request ID: {request_id}"
            )

            # Add response headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = str(request_id)

            return response

        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"EXCEPTION | {request.method} | {request.url.path} | "
                f"Time: {process_time:.3f}s | "
                f"Error: {str(exc)} | "
                f"Request ID: {request_id}",
                exc_info=True,
            )
            raise


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log authentication and authorization events."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log security-related events."""
        auth_header = request.headers.get("authorization", "")
        
        # Log auth endpoints specifically
        if "/auth/" in request.url.path:
            method = request.method
            path = request.url.path
            
            # Avoid logging sensitive data
            if method == "POST" and path == "/api/v1/auth/register":
                logger.info(f"AUTH_EVENT | Registration attempt | IP: {request.client.host}")
            elif method == "POST" and path == "/api/v1/auth/login":
                logger.info(f"AUTH_EVENT | Login attempt | IP: {request.client.host}")
            elif method == "POST" and path == "/api/v1/auth/logout":
                logger.info(f"AUTH_EVENT | Logout event | IP: {request.client.host}")
            elif method == "GET" and path == "/api/v1/auth/me":
                logger.debug(f"AUTH_EVENT | Current user fetch | Token present: {bool(auth_header)}")

        response = await call_next(request)
        return response
