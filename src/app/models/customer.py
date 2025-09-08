from datetime import date
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from . import core


class Customer(core.IntegerPKMixin, core.CreatedUpdatedMixin, SQLModel, table=True):
    __tablename__ = 'customer'

    auth_user_id: UUID = Field(foreign_key='auth_user.id')
    auth_user: 'AuthUser' = Relationship(back_populates='customer', sa_relationship_kwargs={'uselist': False})

    birth_date: date

    bookings: Optional['Booking'] = Relationship(back_populates='customer')
