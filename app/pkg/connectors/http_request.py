"""Request to API with HMAC encryption or X-ACCESS-TOKEN header
authentication."""

import hashlib
import hmac
import json
from typing import Any, Literal

import httpx
import pydantic
from pydantic.types import SecretStr

from app.pkg.logger import get_logger
from app.pkg.models.base import BaseModel
from app.pkg.models.v1.exceptions.client import BaseClientException

__all__ = ["HttpRequests"]


class HttpRequests:
    """Request to API with HMAC encryption or X-ACCESS-TOKEN header
    authentication."""

    client_name: str
    token: pydantic.SecretStr
    hmac_encrypt_key: pydantic.SecretStr
    url: pydantic.AnyUrl

    def __init__(
        self,
        api_url: pydantic.AnyUrl,
        hmac_encrypt_key: pydantic.SecretStr = None,
        x_api_token: pydantic.SecretStr = None,
    ):
        if not any(
            (
                hmac_encrypt_key,
                x_api_token,
            ),
        ):
            """In case we don't have any auth method.

            - we can't init client.
            """
            raise BaseClientException(
                client_name=self.client_name,
                status_code=500,
                message="Error on Clients Connector init.",
            )
        self.token = x_api_token
        self.url = api_url
        self.hmac_encrypt_key = hmac_encrypt_key
        self.client_name = self.__class__.__name__
        self.__logger = get_logger(__name__)

    def _encrypt(self, model: Any, digestmod: hashlib = hashlib.sha256) -> SecretStr:
        """HMAC encryption for request body.

        Args:
            model: Model for encrypt. Can be BaseModel or str (cause we use __parse_data_to_encrypt method)
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
            model: Model for encrypt. Can be BaseModel or str. Other types are not allowed now.

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
        method: Literal["GET", "POST", "DELETE", "PATCH"],
        path: str = None,
        headers: dict = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Do request to API.
        In case we don't have custom headers - we use X-ACCESS-TOKEN header. It's default on our project.
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
        else:
            headers.update({"X-ACCESS-TOKEN": self.token.get_secret_value()})
        async with httpx.AsyncClient(
            headers=headers,
        ) as client:
            try:
                response = await client.request(
                    method=method,
                    url=f"{self.url}/{path}",
                    **kwargs,
                )
                self.__logger.exception("Error to get data %s.", response)
            except httpx.HTTPError as e:
                self.__logger.exception("Request failed %s", str(e))
                raise BaseClientException(
                    client_name=self.client_name,
                    message=str(e),
                    status_code=503,
                ) from e

            if response.is_success:
                return response
            else:
                self.__logger.exception("Request isn't success %s", response.text)
                raise BaseClientException(
                    client_name=self.client_name,
                    status_code=response.status_code,
                    message=response.text,
                )
