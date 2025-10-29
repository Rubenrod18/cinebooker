from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import Field, Relationship, SQLModel

from ..utils.constants import BaseEnum
from .core import CreatedUpdatedMixin, IntegerPKMixin


class PaymentProvider(BaseEnum):
    PAYPAL = 'paypal'
    STRIPE = 'stripe'


class PaymentStatus(BaseEnum):
    """Payment status enum.

    PENDING: booking is pending to pay by the customer.
    COMPLETED: booking is paid by the customer.
    FAILED: there was a problem getting paid.
    CANCELED: booking is canceled. For example: the customer didn't complete or cancel the payment process.

    """

    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class Payment(IntegerPKMixin, CreatedUpdatedMixin, SQLModel, table=True):
    __tablename__ = 'payment'

    booking_id: UUID = Field(foreign_key='booking.id')
    booking: 'Booking' = Relationship(back_populates='payments', sa_relationship_kwargs={'uselist': False})

    provider: PaymentProvider = Field(
        sa_column=sa.Column(
            sa.Enum(
                PaymentProvider,
                name='paymentprovider',
                values_callable=lambda enum: [e.value for e in enum],
                create_type=True,
            ),
            nullable=False,
        )
    )
    provider_payment_id: str | None = Field(default=None)
    provider_metadata: dict | None = Field(sa_column=sa.Column(MutableDict.as_mutable(sa.JSON), default=dict))

    amount: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    currency: str
    status: PaymentStatus = Field(
        sa_column=sa.Column(
            sa.Enum(
                PaymentStatus,
                name='paymentstatus',
                values_callable=lambda enum: [e.value for e in enum],
                create_type=True,
            ),
            nullable=False,
        )
    )
