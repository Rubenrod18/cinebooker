import uuid
from datetime import datetime, UTC
from typing import ClassVar

from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, SQLModel


class IntegerPKMixin(SQLModel):
    __abstract__ = True

    id: int = Field(primary_key=True)


class UUIDPKMixin(SQLModel):
    __abstract__ = True

    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)


class CreatedUpdatedMixin(SQLModel):
    __abstract__ = True

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SoftDeleteMixin(SQLModel):
    __abstract__ = True

    deleted_at: datetime | None = Field(default=None)

    # NOTE: ClassVar ensures Pydantic ignores these
    is_deleted: ClassVar[hybrid_property]
    is_not_deleted: ClassVar[hybrid_property]

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @hybrid_property
    def is_not_deleted(self) -> bool:
        return self.deleted_at is None


class InactiveMixin(SQLModel):
    """Mixin to add active/inactive functionality to a SQLModel model."""

    __abstract__ = True

    inactive_at: datetime | None = Field(default=None)

    def active(self) -> None:
        self.inactive_at = None

    def inactive(self, when: datetime | None = None) -> None:
        self.inactive_at = when or datetime.now(UTC)

    is_actived: ClassVar[hybrid_property]
    is_inactived: ClassVar[hybrid_property]

    @hybrid_property
    def is_actived(self) -> bool:
        return self.inactive_at is None

    @hybrid_property
    def is_inactived(self) -> bool:
        return self.inactive_at is not None
