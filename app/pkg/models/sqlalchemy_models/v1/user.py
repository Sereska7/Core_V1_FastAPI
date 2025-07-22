"""SQlAlchemy model for user."""

from datetime import datetime
from typing import Optional
from uuid import UUID as UUIDType

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.pkg.models.sqlalchemy_models import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
