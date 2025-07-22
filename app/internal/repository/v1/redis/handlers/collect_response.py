"""Collect response from aiopg and convert it to an annotated model."""

import json
from functools import wraps
from types import NoneType
from typing import Any, Callable, List, Optional, Type, Union, get_args, get_origin

from pydantic import TypeAdapter

from app.internal.repository.v1.redis.handlers.handle_exception import handle_exception
from app.pkg.models.base import Model
from app.pkg.models.v1.exceptions.repository import EmptyResult

__all__ = ["collect_response"]


def collect_response(fn) -> Callable[..., Model]:
    """Convert response from aioredis to an annotated model.

    Args:
        fn:
            Target function that contains a query in redis.

    Warnings:
        The function must return a single row or a list of rows in format like::

            >>> ({"key": "value"}, ...)

    Returns:
        The model that is specified in type hints of `fn`.

    Raises:
        EmptyResult: when a query of `fn` returns None.
    """

    @wraps(fn)
    @handle_exception
    async def inner(
        *args: object,
        **kwargs: object,
    ) -> List[type[Model]] | type[Model]:
        """Inner function of :func:`.collect_response`. Convert response from
        aiopg to an annotated model.

        Args:
            *args:
                Positional arguments.
            **kwargs:
                Keyword arguments.

        Raises:
            EmptyResult: when a query of `fn` returns None.

        Returns:
            The model that is specified in type hints of `fn`.
        """

        response = await fn(*args, **kwargs)
        return await process_response(fn, response, *args, **kwargs)

    return inner


async def process_response(
    fn: Callable,
    response: Any,
    *args: object,
    **kwargs: object,
) -> Union[List[Type[Model]], Type[Model], None]:
    """Process the response and convert it to the appropriate model.

    Args:
        fn: The target function.
        response: The response from the database.

    Returns:
        The processed response in the form of the model.
    """

    return_annotation = kwargs.get("result_model")
    if return_annotation is None or return_annotation is NoneType:
        return None

    origin = get_origin(return_annotation)
    is_optional = __is_optional_type(origin)

    if is_optional and response:
        return_annotation = __get_optional_type(return_annotation)
    elif is_optional and not response:
        return None

    if origin is list and not response:
        return []

    if not response:
        raise EmptyResult

    adapter = TypeAdapter(return_annotation)

    return adapter.validate_python(
        await __convert_response(
            response=response,
            annotations=str(return_annotation),
        ),
    )


def __is_optional_type(origin) -> bool:
    """Check if the type is Optional or Union.
    Args:
        origin: Type origin.

    Returns: True if the type is Optional or Union, False otherwise.
    """

    return origin in (
        Optional,
        Union,
    )


async def __convert_response(response: bytes | bytearray, annotations: str):
    """Converts the response of the request to List of models or to a single
    model.

    Args:
        response:
            Response of an aioredis query.
        annotations:
            Annotations of `fn`.

    Returns:
        List[`Model`] if List is specified in the type annotations,
        or a single `Model` if `Model` is specified in the type annotations.
    """

    decoded = response.decode("utf-8")
    response = json.loads(decoded)

    if isinstance(response, list) or annotations.replace("typing.", "").startswith(
        "List",
    ):
        return [await __convert_memory_viewer(item) for item in response]

    return await __convert_memory_viewer(response)


async def __convert_memory_viewer(r: dict[str, bytes]) -> dict[str, bytes]:
    """Convert memory viewer in bytes.

    Notes:
        aiopg returns memory viewer in query response,
        when in database type of cell `bytes`.

    Returns:
        Converted to model string.
    """

    for key, value in r.items():
        if isinstance(value, memoryview):
            r[key] = value.tobytes()
    return r


def __get_optional_type(return_annotation) -> Type[Model]:
    """Get the type of Optional or Union.
    Args:
        return_annotation: Type annotation.

    Returns: Type of the Optional or Union.
    """
    origin = get_origin(return_annotation)
    if origin not in (Optional, Union):
        return return_annotation
    args = get_args(return_annotation)
    for arg in args:
        if arg is type(None):
            continue
        return arg
