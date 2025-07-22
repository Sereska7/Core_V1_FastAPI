"""Clients exceptions."""

from starlette import status

from app.pkg.models.base import BaseAPIException
from app.pkg.models.types.strings import NotEmptyStr

__all__ = [
    "BaseClientException",
    "BaseExceptionFromClient",
    "BadRequestFromClient",
    "UnprocessableEntity",
]


class BaseClientException(BaseAPIException):
    def __init__(self, client_name: str, status_code: int = 503, message: str = ""):
        super().__init__(
            message=NotEmptyStr(
                f"{client_name} is not available now"
                f" status_code: {status_code} message: {message}",
            ),
        )


class BaseExceptionFromClient(BaseAPIException):
    message = "Service is not available now."
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class BadRequestFromClient(BaseAPIException):
    message = "Bad request from client."
    status_code = status.HTTP_400_BAD_REQUEST


class UnprocessableEntity(BaseAPIException):
    message = "Unprocessable entity."
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
