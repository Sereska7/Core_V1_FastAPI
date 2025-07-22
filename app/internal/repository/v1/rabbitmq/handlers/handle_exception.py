"""Handle RabbitMQ Query Exceptions."""

from typing import AsyncGenerator, Callable

import aio_pika

from app.pkg.models.base import Model

__all__ = ["handle_exception"]


def handle_exception(
    func: Callable[..., Model],
) -> Callable[..., AsyncGenerator[Model, None]]:
    """Decorator Catching RabbitMQ Query Exceptions.

    Args:
        func: callable function object.

    Examples:
        For example, if you have a function that contains a query in rabbitmq,
        decorator ``handle_exception`` will catch the exceptions that can be
    Returns:
        Result of call function.
    Raises:
        EmptyResult: Function returned epmty result.
        AMQPError: AMQP exception.
        DriverError: Unexcepted rabbit exception.
    """

    async def wrapper(*args: object, **kwargs: object) -> AsyncGenerator[Model, None]:
        """Inner function. Catching RabbitMQ Query Exceptions.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Result of call function.
        Raises:
            EmptyResult: Function returned epmty result.
            AMQPError: AMQP exception.
            DriverError: Unexcepted rabbit exception.
        """

        try:
            async for i in func(*args, **kwargs):
                yield i
        except aio_pika.exceptions.AMQPError as error:
            raise error
        except Exception as error:
            raise error

    return wrapper
