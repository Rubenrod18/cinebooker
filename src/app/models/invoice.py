from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from ..utils.constants import BaseEnum
from . import core


class InvoiceStatus(BaseEnum):
    ISSUED = 'issued'
    PAID = 'paid'
    REFUNDED = 'refunded'


class Invoice(core.IntegerPKMixin, core.CreatedUpdatedMixin, table=True):
    __tablename__ = 'invoice'

    booking_id: UUID = Field(foreign_key='booking.id')
    booking: 'Booking' = Relationship(back_populates='invoice', sa_relationship_kwargs={'uselist': False})

    code: str
    currency: str
    total_base_price: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    vat_rate: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    total_vat_price: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    total_price: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    status: InvoiceStatus = Field(
        sa_column=sa.Column(
            sa.Enum(
                InvoiceStatus,
                name='invoicestatus',
                values_callable=lambda enum: [e.value for e in enum],
                create_type=True,
            ),
            nullable=False,
        )
    )

    invoice_items: list['InvoiceItem'] | None = Relationship(back_populates='invoice')


class InvoiceItem(core.IntegerPKMixin, core.CreatedUpdatedMixin, SQLModel, table=True):
    __tablename__ = 'invoice_item'

    invoice_id: int = Field(foreign_key='invoice.id')
    invoice: 'Invoice' = Relationship(back_populates='invoice_items', sa_relationship_kwargs={'uselist': False})

    description: str
    quantity: int
    unit_price: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    base_price: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    vat_rate: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    vat_price: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    total_price: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
