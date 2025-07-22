"""Handle Postgresql Query Exceptions."""

from typing import Any, Callable, Coroutine

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.pkg.logger import get_logger
from app.pkg.models.base import Model
from app.pkg.models.v1.exceptions.repository import DriverError, UniqueViolation

logger = get_logger(__name__)


def handle_exception(
    func: Callable[..., Model],
) -> Callable[[tuple[object, ...], dict[str, object]], Coroutine[Any, Any, Model]]:
    """Decorator catching SQLAlchemy async exceptions."""

    async def wrapper(*args: object, **kwargs: object) -> Model:
        try:
            return await func(*args, **kwargs)
        except IntegrityError as error:
            if "unique constraint" in str(error).lower():
                logger.exception(f"Unique constraint violation: {error}")
                raise UniqueViolation from error

            logger.exception(f"Integrity error: {error}")
            raise DriverError(error_details=str(error)) from error

        except SQLAlchemyError as error:
            logger.exception(f"SQLAlchemy error: {error}")
            raise DriverError(error_details=str(error)) from error

    return wrapper
