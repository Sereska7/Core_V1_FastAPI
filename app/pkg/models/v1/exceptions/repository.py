"""Exceptions for repository layer."""

from fastapi import status

from app.pkg.models.base import BaseAPIException

__all__ = [
    "UniqueViolation",
    "EmptyResult",
    "DriverError",
    "InsertChangelogException",
]


class UniqueViolation(BaseAPIException):
    message = "Not unique."
    status_code = status.HTTP_409_CONFLICT


class EmptyResult(BaseAPIException):
    message = "Empty result."
    status_code = status.HTTP_404_NOT_FOUND


class DriverError(BaseAPIException):
    """Exception for internal driver errors."""

    message = "Internal driver error."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_details: str = None

    def __init__(self, error_details: str = None):
        """In case of message is None, a default message will be used.

        Args:
            details: Details of exception raised from driver.
        """

        if error_details:
            self.error_details = error_details

        super().__init__()


class InsertChangelogException(BaseAPIException):
    status_code = 500
    message = (
        "Result is not a BaseModel instance. "
        "Ensure that @insert_changelog is above the @collect_response method"
    )
