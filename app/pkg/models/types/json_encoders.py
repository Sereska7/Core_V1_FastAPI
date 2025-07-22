"""Custom types with JSON encoders for specific types."""

from datetime import date, datetime
from typing import Annotated

import pydantic

from app.pkg.models import types

JSONSecretStr = Annotated[
    pydantic.SecretStr,
    pydantic.PlainSerializer(
        lambda v: v.get_secret_value(),
        return_type=str,
        when_used="json-unless-none",
    ),
]

JSONSecretBytes = Annotated[
    pydantic.SecretBytes,
    pydantic.PlainSerializer(
        lambda v: v.get_secret_value(),
        return_type=str,
        when_used="json-unless-none",
    ),
]

JSONEncryptedSecretBytes = Annotated[
    types.EncryptedSecretBytes,
    pydantic.PlainSerializer(
        lambda v: v.get_secret_value(),
        return_type=str,
        when_used="json-unless-none",
    ),
]

JSONBytes = Annotated[
    bytes,
    pydantic.PlainSerializer(
        lambda v: v.decode(),
        return_type=str,
        when_used="json-unless-none",
    ),
]

JSONDatetime = Annotated[
    datetime,
    pydantic.PlainSerializer(
        lambda v: int(v.timestamp()),
        return_type=int,
        when_used="json-unless-none",
    ),
]

JSONDate = Annotated[
    date,
    pydantic.PlainSerializer(
        lambda v: int(v.timestamp()),
        return_type=int,
        when_used="json-unless-none",
    ),
]
