from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from ..utils.constants import BaseEnum
from . import core


class BookingStatus(BaseEnum):
    PENDING_PAYMENT = 'pending_payment'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'


class Booking(core.UUIDPKMixin, core.CreatedUpdatedMixin, SQLModel, table=True):
    __tablename__ = 'booking'

    customer_id: int = Field(foreign_key='customer.id')
    customer: 'Customer' = Relationship(back_populates='bookings', sa_relationship_kwargs={'uselist': False})

    showtime_id: UUID = Field(foreign_key='showtime.id')
    showtime: 'Showtime' = Relationship(back_populates='bookings', sa_relationship_kwargs={'uselist': False})

    discount_id: int | None = Field(foreign_key='discount.id')
    discount: Optional['Discount'] = Relationship(back_populates='bookings', sa_relationship_kwargs={'uselist': False})

    status: BookingStatus = Field(
        sa_column=sa.Column(
            sa.Enum(
                BookingStatus,
                name='bookingstatus',
                values_callable=lambda enum: [e.value for e in enum],
                create_type=True,
            ),
            nullable=False,
        )
    )
    expired_at: datetime | None

    booking_seats: list['BookingSeat'] | None = Relationship(back_populates='booking')
    payments: list['Payment'] | None = Relationship(back_populates='booking')
    invoice: Optional['Invoice'] = Relationship(back_populates='booking')


class BookingSeat(core.IntegerPKMixin, SQLModel, table=True):
    __tablename__ = 'booking_seat'

    booking_id: UUID = Field(foreign_key='booking.id')
    booking: 'Booking' = Relationship(back_populates='booking_seats', sa_relationship_kwargs={'uselist': False})

    seat_id: int = Field(foreign_key='seat.id')
    seat: 'Seat' = Relationship(back_populates='booking_seat', sa_relationship_kwargs={'uselist': False})

    base_price: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    vat_rate: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    price_with_vat: Decimal = Field(sa_column=sa.DECIMAL(12, 2))

    ticket: Optional['Ticket'] = Relationship(back_populates='booking_seat', sa_relationship_kwargs={'uselist': False})
