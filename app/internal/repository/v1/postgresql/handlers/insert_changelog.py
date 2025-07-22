"""Module for inserting models into changelog asynchronously."""

from functools import wraps
from typing import Any, Callable, List, Type, Union

from dependency_injector.wiring import inject

from app.internal.repository.repository import Repository
from app.pkg.logger import get_logger
from app.pkg.models.base import BaseModel
from app.pkg.models.v1.exceptions.repository import (
    DriverError,
    InsertChangelogException,
)

logger = get_logger(__name__)


def __convert_to_model(model_class: Type[BaseModel], data: dict) -> BaseModel:
    """Convert a dictionary to an instance of the model class."""
    return model_class(**data)


async def __create(repository_instance: Repository, to_insert: List[BaseModel]) -> None:
    for model in to_insert:
        try:
            await repository_instance.create(model)
        except DriverError as e:
            logger.exception("Failed to insert model %s into changelog.", type(model))
            raise InsertChangelogException from e


def insert_changelog(
    repository: Type[Repository],
) -> Callable[[Callable[..., BaseModel | list[BaseModel]]], Callable[..., Any]]:
    """Decorator for inserting models into changelog asynchronously.
    Args:
        repository: repository class to be injected.

    Returns: Inner decorator.
    """

    def insert_changelog_inner(
        function: Callable[..., Union[BaseModel, List[BaseModel]]],
    ) -> Callable:
        @wraps(function)
        @inject
        async def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Union[BaseModel, List[BaseModel]]:
            repository_instance: Repository = repository()
            result: Union[BaseModel, List[BaseModel]] = await function(
                *args,
                **kwargs,
            )

            if isinstance(result, BaseModel):
                to_insert = [result]
            elif isinstance(result, list):
                to_insert = result
            else:
                raise InsertChangelogException()

            await __create(repository_instance, to_insert)

            return result

        return wrapper

    return insert_changelog_inner
