"""V1 clients."""

from dependency_injector import containers, providers

from app.pkg.clients import v1

__all__ = ["Clients"]


class Clients(containers.DeclarativeContainer):
    """Container with clients."""

    v1 = providers.Container(v1.Clients)
