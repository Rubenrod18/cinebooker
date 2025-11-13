from decimal import Decimal
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..di_container import ServiceDIContainer
from ..exceptions import NotFoundException
from ..models.booking import Booking, BookingStatus
from ..models.invoice import InvoiceStatus
from ..repositories.booking_repository import BookingRepository
from . import booking_schemas, core


class InvoiceResponseSchema(core.IntegerPKMixin, core.CreatedUpdatedMixin, BaseModel):
    id: int = Field(exclude=True)
    booking_id: UUID
    code: str
    currency: str
    total_base_price: Decimal
    vat_rate: Decimal
    total_vat_price: Decimal
    total_price: Decimal
    status: InvoiceStatus

    model_config = ConfigDict(from_attributes=True)


class BookingIdRequestSchema(booking_schemas.BookingIdRequestSchema):
    @field_validator('booking_id')
    @classmethod
    @inject
    def validate_booking_id(
        cls, booking_id: UUID, booking_repository: BookingRepository = Provide[ServiceDIContainer.booking_repository]
    ) -> UUID:
        booking = booking_repository.find_one_with_seats(
            Booking.id == booking_id, Booking.status == BookingStatus.PENDING_PAYMENT
        )

        if not booking:
            raise NotFoundException(description='Booking not found')

        cls._booking = booking
        return booking_id
