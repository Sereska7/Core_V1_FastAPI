"""RabbitMQ repository container module."""

from dependency_injector import containers, providers
from app.internal.repository.v1.rabbitmq.base_repository import BaseRepository


class Repositories(containers.DeclarativeContainer):
    """RabbitMQ repository container."""

    base_repository = providers.Factory(BaseRepository)
