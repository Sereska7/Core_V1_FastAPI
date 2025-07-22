"""Server configuration."""

from fastapi import FastAPI

from app.internal.pkg.middlewares.handle_http_exceptions import (
    handle_api_exceptions,
    handle_drivers_exceptions,
    handle_internal_exception,
)
from app.internal.routes import __routes__
from app.pkg.models.base import BaseAPIException
from app.pkg.models.types.fastapi import FastAPITypes
from app.pkg.models.v1.exceptions.repository import DriverError

__all__ = ["Server"]


class Server:
    """Register all requirements for the correct work of server instance.

    Attributes:
        __app:
            ``FastAPI`` application instance.
    """

    __app: FastAPI

    def __init__(self, app: FastAPI):
        """Initialize server instance. Register all requirements for the
        correct work of server instance.

        Args:
            app:
                ``FastAPI`` application instance.
        """

        self.__app = app
        self._register_routes(app)
        self._register_http_exceptions(app)

    def get_app(self) -> FastAPI:
        """Getter of the current application instance.

        Returns:
            ``FastAPI`` application instance.
        """
        return self.__app

    @staticmethod
    def _register_routes(app: FastAPITypes.instance) -> None:
        """Include routers in ``FastAPI`` instance from ``__routes__``.

        Args:
            app:
                ``FastAPI`` application instance.

        Returns:
            None
        """

        __routes__.register_routes(app)

    @staticmethod
    def _register_http_exceptions(app: FastAPITypes.instance) -> None:
        """Register http exceptions.

        instance handle ``BaseApiExceptions`` raises inside functions.

        Args:
            app:
                ``FastAPI`` application instance.

        Returns:
            None
        """

        app.add_exception_handler(BaseAPIException, handle_api_exceptions)
        app.add_exception_handler(DriverError, handle_drivers_exceptions)
        app.add_exception_handler(Exception, handle_internal_exception)
