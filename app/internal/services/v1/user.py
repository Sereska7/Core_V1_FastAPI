"""Models for Folder object."""

from logging import Logger

from app.internal.repository.v1.postgresql.user import UserRepository
from app.pkg.logger import get_logger
from app.pkg.models import v1 as models
from app.pkg.models.v1.exceptions.repository import DriverError

__all__ = ["UserService"]


class UserService:
    """"""

    user_repository: UserRepository
    __logger: Logger = get_logger(__name__)

    async def get_users(self) -> list[models.User]:
        """Retrieves a list of folders from the repository based on the
        provided query.

        Args:
            query (models.FolderReadQuery): The query containing the parameters for filtering folders.

        Returns:
            list[models.Folder]: A list of folder models that match the query.
        """

        try:
            return await self.user_repository.read()
        except DriverError as exc:
            self.__logger.exception("Error reading folder")
            raise Exception from exc
