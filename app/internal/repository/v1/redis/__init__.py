"""Redis repositories module."""

from dependency_injector import containers, providers

from app.internal.repository.v1.redis.base_repository import BaseRedisRepository


class RedisRepositories(containers.DeclarativeContainer):
    base_redis_repository = providers.Factory(BaseRedisRepository)
