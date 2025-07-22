"""User repository for PostgresSQL database."""

from abc import ABC
from typing import Type, TypeVar

from app.internal.repository.v1.redis.connection import get_connection
from app.internal.repository.v1.redis.handlers.collect_response import collect_response

__all__ = ["BaseRedisRepository"]

from app.pkg.models.base import BaseModel

BaseRepository = TypeVar("BaseRepository", bound="BaseRedisRepository")


class BaseRedisRepository(ABC):
    """Repository for alert manager system."""

    @staticmethod
    async def create(
        redis_key: str,
        redis_value: str,
        expire_time: int | None = None,
    ):
        async with get_connection() as connect:
            await connect.set(redis_key, redis_value)
            if expire_time:
                await connect.expire(redis_key, expire_time)

    @collect_response
    async def read(
        self,
        redis_key: str,
        result_model: Type[BaseModel],  # pylint: disable=unused-argument
    ) -> Type[BaseModel]:
        async with get_connection() as connect:
            return await connect.get(redis_key)
