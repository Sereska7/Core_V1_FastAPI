"""Container with rabbitmq connector."""

from dependency_injector import containers, providers

from app.pkg.connectors.rabbitmq.resource import RabbitMQ
from app.pkg.settings import settings

__all__ = ["RabbitMQContainer"]


class RabbitMQContainer(containers.DeclarativeContainer):
    """Declarative container with rabbitmq connector."""

    configuration = providers.Configuration()
    configuration.from_dict(settings.model_dump())

    connector = providers.Resource(
        RabbitMQ,
        dsn=configuration.RABBITMQ.DSN,
        max_size=configuration.RABBITMQ.MAX_CONNECTION,
    )
