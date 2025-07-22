"""Module for request ID route class."""

from typing import Callable
from uuid import UUID, uuid4

from starlette.requests import Request
from starlette.responses import Response

from app.pkg.models.base.logger_api_route import LoggerRoute


class RequestIDRoute(LoggerRoute):
    """Middleware for assigning and managing request IDs.

    Extends the LoggerRoute to add request IDs to the request body for write
    methods (`POST`, `PUT`, `PATCH`) and to include the request ID in the response
    headers for tracing purposes.
    """

    def get_route_handler(self) -> Callable:
        """Override the route handler to add request ID functionality.

        Returns:
            Callable: The customized route handler with request ID logic.
        """
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Handle incoming requests and outgoing responses with request
            IDs.

            Args:
                request (Request): The incoming HTTP request.

            Returns:
                Response: The HTTP response with the `X-Request-ID` header added.
            """
            request_id = str(uuid4())
            request.state.request_id = UUID(request_id)

            response: Response = await original_route_handler(request)
            response.headers["X-Request-ID"] = request_id
            return response

        return custom_route_handler
