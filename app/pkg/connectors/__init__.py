"""All connectors in declarative container."""

from dependency_injector import containers, providers

from app.pkg.connectors.postgresql import PostgresSQL
from app.pkg.connectors.rabbitmq.rabbitmq import RabbitMQContainer
from app.pkg.connectors.redis import RedisContainer
from app.pkg.settings import settings

__all__ = ["Connectors", "PostgresSQL"]


class Connectors(containers.DeclarativeContainer):
    """Declarative container with all connectors."""

    configuration = providers.Configuration(name="settings")
    configuration.from_dict(settings.model_dump())

    postgresql: PostgresSQL = providers.Container(PostgresSQL)
    rabbitmq: RabbitMQContainer = providers.Container(RabbitMQContainer)
    redis: RedisContainer = providers.Container(RedisContainer)
