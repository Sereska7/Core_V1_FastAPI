"""Handlers that handle internal error raise and returns ``http json``
response.

Examples:
    For example, if in some level in code you raise error inherited by
    :class:`.BaseAPIException`::

        >>> ...  # exceptions.py
        >>> class E(BaseAPIException):
        ...     status_code = status.HTTP_200_OK
        ...     message = "test error."

        >>> ...  # some_file.py
        >>> async def some_internal_function():
        ...     raise E

    When ``some_internal_function`` called, exception will process by
    ``handle_api_exceptions`` and returns a json object with status code 200::

        {
            "message": "test error."
        }
"""

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.pkg.logger import get_logger
from app.pkg.models.base import BaseAPIException
from app.pkg.models.v1.exceptions.repository import DriverError

__all__ = [
    "handle_internal_exception",
    "handle_api_exceptions",
    "handle_drivers_exceptions",
]

logger = get_logger(__name__)


def handle_drivers_exceptions(request: Request, exc: DriverError) -> JSONResponse:
    """Handle all internal exceptions to :class:`.DriverError`.

    Args:
        request:
            ``Request`` instance.
        exc:
            Exception inherited from :class:`.DriverError`.

    Returns:
        ``JSONResponse`` object with status code 500.
    """

    request_id = getattr(request.state, "request_id", None)
    log_data = {
        "type": "Driver Error",
        "request_id": str(request_id),
        "method": request.method,
        "path": request.url.path,
        "headers": dict(request.headers),
        "error": str(exc),
    }
    logger.error("Driver error occurred.", extra={"context": log_data})
    return JSONResponse(
        status_code=500,
        content={
            "error": "Driver error occurred.",
            "details": str(exc),
            "request_id": str(request_id),
        },
    )


def handle_api_exceptions(request: Request, exc: BaseAPIException):
    """Handle all internal exceptions that inherited from
    :class:`.BaseAPIException`.

    Args:
        request:
            ``Request`` instance.
        exc:
            Exception inherited from :class:`.BaseAPIException`.

    Returns:
        ``JSONResponse`` object with status code from ``exc.status_code``.
    """

    request_id = getattr(request.state, "request_id", None)
    log_data = {
        "type": "API Exception",
        "request_id": str(request_id),
        "method": request.method,
        "path": request.url.path,
        "headers": dict(request.headers),
        "error": exc.detail,
        "code": exc.status_code,
    }
    logger.error("API exception occurred.", extra={"context": log_data})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": exc.status_code,
            "request_id": str(request_id),
        },
    )


def handle_internal_exception(request: Request, exc: Exception):
    """Handle all internal unhandled exceptions.

    Args:
        request:
            ``Request`` instance.
        exc:
            ``Exception`` instance.

    Returns:
        ``JSONResponse`` object with status code 500.
    """

    request_id = getattr(request.state, "request_id", None)
    log_data = {
        "type": "Internal Exception",
        "request_id": str(request_id),
        "method": request.method,
        "path": request.url.path,
        "headers": dict(request.headers),
        "error": str(exc),
    }
    logger.exception("Internal exception occurred.", extra={"context": log_data})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error occurred.",
            "request_id": str(request_id),
        },
    )
