"""Container with Redis connector."""

from dependency_injector import containers, providers

from app.pkg.connectors.redis.resource import RedisResource
from app.pkg.settings import settings

__all__ = ["RedisContainer"]


class RedisContainer(containers.DeclarativeContainer):
    """Declarative container with Redis connector."""

    configuration = providers.Configuration(name="settings")
    configuration.from_dict(settings.model_dump())

    connector = providers.Resource(
        RedisResource,
        dsn=configuration.REDIS.DSN,
    )
