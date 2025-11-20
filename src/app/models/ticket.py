from datetime import datetime, UTC

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from ..utils.constants import BaseEnum
from .core import IntegerPKMixin


class TicketBarcodeType(BaseEnum):
    QR = 'qr'  # NOTE: Only this option is used
    CODE128 = 'code128'
    EAN13 = 'ean13'


class TicketStatus(BaseEnum):
    ISSUED = 'issued'
    REDEEMED = 'redeemed'


class Ticket(IntegerPKMixin, SQLModel, table=True):
    __tablename__ = 'ticket'

    booking_seat_id: int = Field(foreign_key='booking_seat.id')
    booking_seat: 'BookingSeat' = Relationship(back_populates='ticket', sa_relationship_kwargs={'uselist': False})

    barcode_value: str
    barcode_type: TicketBarcodeType = Field(
        sa_column=sa.Column(
            sa.Enum(
                TicketBarcodeType,
                name='ticketbarcodetype',
                values_callable=lambda enum: [e.value for e in enum],
                create_type=True,
            ),
            nullable=False,
        )
    )
    status: TicketStatus = Field(
        sa_column=sa.Column(
            sa.Enum(
                TicketStatus,
                name='ticketstatus',
                values_callable=lambda enum: [e.value for e in enum],
                create_type=True,
            ),
            nullable=False,
        )
    )
    issued_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={'server_default': sa.func.now()},  # pylint: disable=not-callable
        nullable=False,
    )
    redeemed_at: datetime | None

    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('barcode_value'),
    )
