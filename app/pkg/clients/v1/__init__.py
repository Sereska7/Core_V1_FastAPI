"""All connectors in declarative container."""

from dependency_injector import containers, providers

from app.pkg.settings import settings

__all__ = [
    "Clients",
]


class Clients(containers.DeclarativeContainer):
    """Declarative container with clients."""

    configuration = providers.Configuration(name="settings")
    configuration.from_dict(settings.model_dump())
