"""User models."""

from datetime import datetime
from uuid import UUID

from pydantic.fields import Field

from app.pkg.models.base import BaseModel
from app.pkg.models.base.optional_field import create_optional_fields_class

__all__ = [
    "User",
]


class BaseUser(BaseModel):
    """Base model for User."""


class UserFields:
    """User fields."""

    id: UUID = Field(
        description="User ID.",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    email: str = Field(
        description="Email of the user.",
        examples=["lolekeektop1@mail.ru"],
    )
    hashed_password: str = Field(
        description="Password of the user.",
        examples=["Documents", "Photos", "Work"],
    )
    is_active: bool = Field(
        description="Indicates whether the user (or entity) is active.",
        examples=[True, False],
    )
    created_at: datetime = Field(
        description="Timestamp when the record was created.",
        examples=["2025-07-21T16:30:00Z"],
    )
    updated_at: datetime = Field(
        description="Timestamp when the record was last updated.",
        examples=["2025-07-21T16:30:00Z"],
    )


OptionalFolderFields = create_optional_fields_class(UserFields)


class User(BaseUser):
    """User model."""

    id: UUID = UserFields.id
    email: str = UserFields.email
    hashed_password: str = UserFields.hashed_password
    is_active: bool = UserFields.is_active
    created_at: datetime = UserFields.created_at
    updated_at: datetime = UserFields.updated_at
