"""Custom exception handlers for Syria GPT API."""

import logging
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class SyriaGPTException(Exception):
    """Base exception class for Syria GPT."""

    def __init__(self, message: str, status_code: int = 500, details: Union[str, dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(SyriaGPTException):
    """Authentication related errors."""

    def __init__(self, message: str = "Authentication failed", details: Union[str, dict] = None):
        super().__init__(message, 401, details)


class AuthorizationError(SyriaGPTException):
    """Authorization related errors."""

    def __init__(self, message: str = "Access forbidden", details: Union[str, dict] = None):
        super().__init__(message, 403, details)


class ValidationError(SyriaGPTException):
    """Data validation errors."""

    def __init__(self, message: str = "Validation error", details: Union[str, dict] = None):
        super().__init__(message, 422, details)


class DatabaseError(SyriaGPTException):
    """Database operation errors."""

    def __init__(self, message: str = "Database error", details: Union[str, dict] = None):
        super().__init__(message, 500, details)


async def syria_gpt_exception_handler(request: Request, exc: SyriaGPTException) -> JSONResponse:
    """Handle custom Syria GPT exceptions."""
    logger.error(f"SyriaGPT exception: {exc.message}", extra={"details": exc.details})

    content = {
        "error": True,
        "message": exc.message,
        "status_code": exc.status_code,
    }

    if exc.details:
        content["details"] = exc.details

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Validation error",
            "status_code": 422,
            "details": exc.errors(),
        },
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors."""
    logger.error(f"Database error: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
        },
    )
