from datetime import datetime, UTC
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from .core import InactiveMixin, UUIDPKMixin


class AuthUser(InactiveMixin, UUIDPKMixin, SQLModel, table=True):
    __tablename__ = 'auth_user'

    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    password: str = Field(..., exclude=True)
    date_joined: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_login: datetime | None

    customer: Optional['Customer'] = Relationship(back_populates='auth_user', sa_relationship_kwargs={'uselist': False})
