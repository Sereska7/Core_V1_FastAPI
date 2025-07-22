"""Handle Redis Query Exceptions."""

from collections.abc import Callable

from redis.asyncio import RedisError

from app.pkg.models.base import Model
from app.pkg.models.v1.exceptions.repository import DriverError, EmptyResult

__all__ = ["handle_exception"]


def handle_exception(func: Callable[..., Model]) -> Callable[..., Model]:
    """Decorator Catching Postgresql Query Exceptions.

    Args:
        func:
            callable function object.

    Returns:
        Result of call function.

    Raises:
        DriverError: Any error during execution query on a database.
    """

    async def wrapper(*args: object, **kwargs: object) -> Model:
        """Inner function. Catching Redis Query Exceptions.

        Args:
            *args:
                Positional arguments.
            **kwargs:
                Keyword arguments.

        Raises:
            DriverError: Any error during execution query in database.

        Returns:
            Result of call function.
        """

        try:
            return await func(*args, **kwargs)
        except EmptyResult as ex:
            raise EmptyResult from ex
        except RedisError as error:
            raise error
        except Exception as ex:
            raise DriverError from ex

    return wrapper
