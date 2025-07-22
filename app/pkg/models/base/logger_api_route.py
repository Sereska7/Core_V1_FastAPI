"""Logger middleware for tracking incoming requests and outgoing responses.

This module provides a `LoggerRoute` class that wraps API route handlers
to log request and response details for internal microservices.
"""

import json
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

from app.pkg.logger import logger


class LoggerRoute(APIRoute):
    """Middleware to log details of requests and responses.

    This class wraps the FastAPI route handler to log information about
    incoming requests and outgoing responses. It captures details such
    as the HTTP method, path, request body, response status code, and
    response body.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the LoggerRoute class."""
        super().__init__(*args, **kwargs)

    @staticmethod
    async def parse_request_data(request: Request) -> dict:
        """Parse the request body into a dictionary.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            dict: The parsed request body, or an empty dictionary if parsing fails.
        """
        try:
            body = await request.body()
            if body:
                return json.loads(body)
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
            return {}

    @staticmethod
    async def log_request(request: Request, data: dict, log):
        """Log details of the incoming request.

        Args:
            request (Request): The incoming HTTP request.
            data (dict): The parsed request body.
            log (Logger): The logger instance used for logging.
        """
        request_id = getattr(request.state, "request_id", None)

        log.info(
            "Incoming request.",
            extra={
                "context": {
                    "method": request.method,
                    "path": str(request.url.path),
                    "request_id": str(request_id),
                    "data": data,
                },
            },
        )

    async def log_response(
        self,
        request: Request,
        response: Response,
        request_data: dict,
        log,
    ):
        """Log details of the outgoing response.

        Args:
            request (Request): The original HTTP request.
            response (Response): The HTTP response returned by the route handler.
            request_data (dict): The parsed request body.
            log (Logger): The logger instance used for logging.
        """
        request_id = getattr(request.state, "request_id", None)
        response_data = await self.parse_response_data(response)

        log.info(
            "Response sent.",
            extra={
                "context": {
                    "method": request.method,
                    "path": str(request.url.path),
                    "request_id": str(request_id),
                    "status_code": response.status_code,
                    "response_data": response_data,
                    "request_data": request_data,
                },
            },
        )

    @staticmethod
    async def parse_response_data(response: Response) -> dict:
        """Parse the response body into a dictionary.

        Args:
            response (Response): The HTTP response.

        Returns:
            dict: The parsed response body, or an empty dictionary if parsing fails.
        """
        try:
            if response.body:
                return json.loads(response.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        return {}

    def get_route_handler(self) -> Callable:
        """Wrap the original route handler to add logging.

        Returns:
            Callable: The customized route handler with logging functionality.
        """
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Custom route handler that logs request and response details.

            Args:
                request (Request): The incoming HTTP request.

            Returns:
                Response: The HTTP response after processing the request.
            """
            log = logger.get_logger(name=request.url.path)
            request_data = await self.parse_request_data(request)

            await self.log_request(request, request_data, log)

            response = await original_route_handler(request)

            await self.log_response(request, response, request_data, log)

            return response

        return custom_route_handler
