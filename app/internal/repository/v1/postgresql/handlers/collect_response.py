"""Collect response module."""

from functools import wraps
from typing import Any, Callable, List, Type, Union, get_args, get_origin, get_type_hints, Optional

from pydantic import TypeAdapter

from app.pkg.models.base import Model
from app.pkg.models.v1.exceptions.repository import EmptyResult
from app.internal.repository.v1.postgresql.handlers.handle_exception import handle_exception


def collect_response(fn) -> Callable:
    @wraps(fn)
    @handle_exception
    async def inner(*args: Any, **kwargs: Any) -> Union[List[Type[Model]], Type[Model], None]:
        response = await fn(*args, **kwargs)
        return await process_response(fn, response)

    return inner


async def process_response(fn: Callable, response: Any) -> Union[List[Type[Model]], Type[Model], None]:
    return_annotation = get_type_hints(fn).get("return")
    if return_annotation is None or return_annotation is type(None):
        return None

    origin = get_origin(return_annotation)
    is_optional = origin is Union and type(None) in get_args(return_annotation)

    # Если опциональный и нет результата — вернуть None
    if is_optional and not response:
        return None

    # Если ожидается список, а результат пуст — вернуть []
    if origin is list and not response:
        return []

    if not response:
        raise EmptyResult

    # Получаем базовый тип из Optional[List[Model]] или Optional[Model]
    base_type = None
    if is_optional:
        # вытаскиваем ненулевой тип из Union
        base_type = [t for t in get_args(return_annotation) if t is not type(None)][0]
    else:
        base_type = return_annotation

    adapter = TypeAdapter(base_type)

    # Если результат — список ORM объектов
    if origin is list:
        # response — это список ORM моделей
        return [adapter.validate_python(obj) for obj in response]

    # Один ORM объект
    return adapter.validate_python(response)
