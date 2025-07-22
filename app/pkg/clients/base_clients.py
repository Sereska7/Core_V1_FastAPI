"""Request to API with HMAC encryption or X-ACCESS-TOKEN header
authentication."""

import hashlib
import hmac
import json
from typing import Any, Literal

import httpx
import pydantic
from pydantic.types import SecretStr
from starlette import status

from app.pkg.logger import get_logger
from app.pkg.models.base import BaseModel
from app.pkg.models.v1.exceptions.base import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnAuthorized,
)
from app.pkg.models.v1.exceptions.client import (
    BadRequestFromClient,
    BaseExceptionFromClient,
    UnprocessableEntity,
)

__all__ = ["BaseClient"]


class BaseClient:
    """Request to API with HMAC encryption or X-ACCESS-TOKEN header
    authentication."""

    client_name: str
    token: pydantic.SecretStr
    hmac_encrypt_key: pydantic.SecretStr
    url: pydantic.AnyUrl

    def __init__(
        self,
    ):
        self.client_name = self.__class__.__name__
        self.__logger = get_logger(__name__)

    def _encrypt(self, model: Any, digestmod: hashlib = hashlib.sha256) -> SecretStr:
        """HMAC encryption for request body.

        Args:
            model: Model for encrypt.
                Can be BaseModel or str (cause we use __parse_data_to_encrypt method)
                Other types are not allowed now.
            digestmod: Hashlib digestmod.

        Returns:
            SecretStr of encrypted data.
        """
        input_hmac = hmac.new(
            key=self.hmac_encrypt_key.get_secret_value().encode("utf-8"),
            msg=self.__parse_data_to_encrypt(model),
            digestmod=digestmod,
        ).hexdigest()
        return SecretStr(input_hmac)

    @staticmethod
    def __parse_data_to_encrypt(model: Any) -> bytes:
        """Parse data to encrypt.

        Args:
            model: Model for encrypt. Can be BaseModel or str.
                Other types are not allowed now.

        Returns:
            Bytes of encrypted data.
        """
        if isinstance(model, BaseModel):
            return json.dumps(
                model.to_dict(show_secrets=True, none_allowed=False),
            ).encode("utf-8")
        elif isinstance(model, str):
            return model.replace("'", '"').encode("utf-8")
        else:
            raise ValueError("We can't change anything in this type.")

    async def do_request(
        self,
        method: Literal["GET", "POST", "DELETE", "PATCH", "PUT"],
        path: str | None = None,
        headers: dict | None = None,
        **kwargs: dict,
    ) -> httpx.Response:
        """
        Do request to API.
        In case we don't have custom headers - we use X-ACCESS-TOKEN header.
        It's default on our project.
        AutoCore and accounting (for example) use HMAC encryption for auth.

        Args:
            method: HTTP method.
            path: Path to API endpoint.
            headers: Headers for request.
            **kwargs: Other params for request.

        Returns:
            Response from API.
        """
        if headers is None:
            headers = {"X-ACCESS-TOKEN": self.token.get_secret_value()}
        async with httpx.AsyncClient(
            headers=headers,
        ) as client:
            try:
                url = f"{self.url}{path}"
                response = await client.request(
                    method=method,
                    url=url,
                    **kwargs,
                )
                self.__logger.debug(
                    "Request to %s was successful. Time elapsed: %s.",
                    url,
                    response.elapsed,
                )
            except httpx.ConnectError as ex:
                self.handle_connection_error(ex)
            except httpx.HTTPError as ex:
                self.handle_client_error(ex)
            return self.handle_response(response)

    def handle_connection_error(self, ex: Exception) -> None:
        raise BaseExceptionFromClient from ex

    def handle_client_error(self, ex: Exception) -> None:
        """Logs and throws client error from exception.

        Args:
            ex (Exception): Exception to throw

        Returns:
            None.
        """
        self.__logger.exception(
            "Error while sending request, client = %s.",
            self.client_name,
            exc_info=ex,
        )
        raise BaseExceptionFromClient from ex

    def handle_response(self, response: httpx.Response) -> httpx.Response:
        """Handle response from API.

        Args:
            response (httpx.Response): Response from API.

        Returns:
            httpx.Response: Response from API.
        """

        http_status = response.status_code

        if response.is_success:
            return response

        error_map = {
            status.HTTP_404_NOT_FOUND: NotFoundError,
            status.HTTP_401_UNAUTHORIZED: UnAuthorized,
            status.HTTP_403_FORBIDDEN: ForbiddenError,
            status.HTTP_409_CONFLICT: ConflictError,
            status.HTTP_400_BAD_REQUEST: BadRequestFromClient,
            status.HTTP_422_UNPROCESSABLE_ENTITY: UnprocessableEntity,
        }

        try:
            response_body = response.json()
        except json.JSONDecodeError:
            response_body = response.text

        self.__logger.error(
            "Request failed. Status: %s, Clients: %s, Response body: %s",
            http_status,
            self.client_name,
            response_body,
        )

        if http_status in error_map:
            raise error_map[http_status](response_body)
        else:
            raise BaseExceptionFromClient(response_body)
