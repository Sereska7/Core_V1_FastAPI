"""Module with base exceptions for the application."""

from starlette import status

from app.pkg.models.base import BaseAPIException

__all__ = [
    "NotFoundError",
    "UnAuthorized",
    "ForbiddenError",
    "ConflictError",
]


class NotFoundError(BaseAPIException):
    message = "Not found."
    status_code = status.HTTP_404_NOT_FOUND


class UnAuthorized(BaseAPIException):
    message = "Not authorized."
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(BaseAPIException):
    message = "Forbidden."
    status_code = status.HTTP_403_FORBIDDEN


class ConflictError(BaseAPIException):
    message = "Conflict."
    status_code = status.HTTP_409_CONFLICT
