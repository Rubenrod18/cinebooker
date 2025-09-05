from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from . import core as c


class Discount(c.IntegerPKMixin, c.InactiveMixin, c.CreatedUpdatedMixin, SQLModel, table=True):
    __tablename__ = 'discount'

    code: str = Field(unique=True)
    description: str
    is_percentage: bool
    amount: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    expires_at: datetime | None
    usage_limit: int | None
    times_used: int | None

    bookings: list['Booking'] | None = Relationship(back_populates='discount')
