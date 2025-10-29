from uuid import UUID

from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, Field, field_validator

from app.di_container import ServiceDIContainer
from app.exceptions import NotFoundException
from app.models.booking import Booking, BookingStatus
from app.repositories.booking_repository import BookingRepository

from . import booking_schemas


class StripeBookingIdRequestSchema(booking_schemas.BookingIdRequestSchema):
    @field_validator('booking_id')
    @classmethod
    @inject
    def validate_booking_id(
        cls, booking_id: UUID, booking_repository: BookingRepository = Provide[ServiceDIContainer.booking_repository]
    ) -> UUID:
        booking = booking_repository.find_one_with_invoices(
            Booking.id == booking_id, Booking.status == BookingStatus.PENDING_PAYMENT
        )

        if not booking:
            raise NotFoundException(description='Booking not found')

        cls._booking = booking
        return booking_id

    @property
    def booking(self) -> Booking:
        return self._booking


class CheckoutSessionRequestSchema(BaseModel):
    mode: str = Field(default='payment', exclude=True)
    line_items: str
    success_url: str = Field(default='/', exclude=True)
    cancel_url: str = Field(default='/', exclude=True)


class CheckoutSessionResponseSchema(BaseModel):
    url: str
