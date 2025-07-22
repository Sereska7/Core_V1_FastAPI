"""V1 service layer."""

from dependency_injector import containers, providers

from app.internal.repository import Repositories
from app.internal.repository.v1 import postgresql, rabbitmq, redis
from app.internal.services.v1.user import UserService
from app.pkg.clients import Clients
from app.pkg.settings import settings


class Services(containers.DeclarativeContainer):
    """Containers with services."""

    configuration = providers.Configuration(name="settings")
    configuration.from_dict(settings.model_dump())

    rabbitmq_repositories: rabbitmq.Repositories = providers.Container(
        Repositories.v1.rabbitmq,
    )  # type: ignore
    redis_repositories: redis.RedisRepositories = providers.Container(
        Repositories.v1.redis,
    )  # type: ignore

    postgres_repositories: postgresql.Repositories = providers.Container(
        Repositories.v1.postgres,
    )  # type: ignore

    clients: Clients = providers.Container(Clients)

    user_service = providers.Factory(UserService)
    user_service.add_attributes(
        user_repository=postgres_repositories.user_repository,
    )
