from decimal import Decimal
from uuid import UUID

import redis
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, PrivateAttr

from ..di_container import ServiceDIContainer
from ..exceptions import NotFoundException, UnprocessableEntityException
from ..models import BookingSeat
from ..models.booking import BookingStatus
from ..repositories.booking_repository import BookingRepository
from ..repositories.booking_seat_repository import BookingSeatRepository
from ..repositories.seat_repository import SeatRepository
from . import core
from .booking_schemas import BookingIdRequestSchema
from .seat_schemas import SeatIdRequestSchema


class BookingSeatCreateSchema(BookingIdRequestSchema, SeatIdRequestSchema):
    base_price: Decimal = Field(..., ge=1)
    vat_rate: Decimal = Field(..., gt=0)

    @field_validator('booking_id')
    @classmethod
    @inject
    def validate_booking_id(
        cls, booking_id: UUID, booking_repository: BookingRepository = Provide[ServiceDIContainer.booking_repository]
    ) -> UUID:
        booking = booking_repository.find_one(
            filter_by={'id': booking_id, 'status': BookingStatus.PENDING_PAYMENT.value}
        )

        if not booking:
            raise NotFoundException(description='Booking not found')

        cls._booking = booking
        return booking_id

    @model_validator(mode='after')
    @inject
    def check_seat_available(
        self,
        booking_seat_repository: BookingSeatRepository = Provide[ServiceDIContainer.booking_seat_repository],
        redis_client: redis.Redis = Provide[ServiceDIContainer.redis_client],
    ):
        if redis_client.exists(f'booking_seat:{self._booking.showtime_id}_{self.seat_id}'):
            raise UnprocessableEntityException(description='Seat is not available')

        if self._booking and not booking_seat_repository.is_seat_available(self._booking.showtime_id, self.seat_id):
            raise UnprocessableEntityException(description='Seat is not available')

        return self


class BookingSeatUpdateSchema(BookingIdRequestSchema, SeatIdRequestSchema):
    booking_id: UUID | None = None
    seat_id: int | None = None
    base_price: Decimal | None = Field(None, ge=1)
    vat_rate: Decimal | None = Field(None, gt=0)

    @field_validator('booking_id')
    @classmethod
    @inject
    def validate_booking_id(
        cls, booking_id: UUID, booking_repository: BookingRepository = Provide[ServiceDIContainer.booking_repository]
    ) -> UUID:
        booking = booking_repository.find_one(
            filter_by={'id': booking_id, 'status': BookingStatus.PENDING_PAYMENT.value}
        )

        if not booking:
            raise NotFoundException(description='Booking not found')

        cls._booking = booking
        return booking_id

    @field_validator('seat_id')
    @classmethod
    @inject
    def validate_seat_id(
        cls, seat_id: int, seat_repository: SeatRepository = Provide[ServiceDIContainer.seat_repository]
    ) -> int:
        if seat_id:
            return super().validate_seat_id(seat_id)

        return seat_id

    @model_validator(mode='after')
    @inject
    def check_seat_available(
        self, booking_seat_repository: BookingSeatRepository = Provide[ServiceDIContainer.booking_seat_repository]
    ):
        if (
            self._booking
            and self.seat_id
            and not booking_seat_repository.is_seat_available(self._booking.showtime_id, self.seat_id)
        ):
            raise UnprocessableEntityException(description='Seat is not available')

        return self


class BookingSeatResponseSchema(core.IntegerPKMixin, core.CreatedUpdatedMixin, BaseModel):
    booking_id: UUID
    seat_id: int
    base_price: Decimal
    vat_rate: Decimal
    price_with_vat: Decimal

    model_config = ConfigDict(from_attributes=True)


class BookingSeatIdRequestSchema(BaseModel):
    booking_seat_id: int
    _booking_seat: BookingSeat | None = PrivateAttr(default=None)

    @field_validator('booking_seat_id')
    @classmethod
    @inject
    def validate_booking_seat_id(
        cls,
        booking_seat_id: int,
        booking_seat_repository: BookingSeatRepository = Provide[ServiceDIContainer.booking_seat_repository],
    ) -> int:
        booking_seat = booking_seat_repository.find_by_id(booking_seat_id)

        if not booking_seat:
            raise NotFoundException(description='BookingSeat not found')

        cls._booking_seat = booking_seat
        return booking_seat_id

    @property
    def booking_seat(self) -> BookingSeat:
        return self._booking_seat


class UpdateBookingSeatIdRequestSchema(BookingSeatIdRequestSchema):
    @field_validator('booking_seat_id')
    @classmethod
    @inject
    def validate_booking_seat_id(
        cls,
        booking_seat_id: int,
        booking_seat_repository: BookingSeatRepository = Provide[ServiceDIContainer.booking_seat_repository],
    ) -> int:
        booking_seat = booking_seat_repository.find_pending_payment_by_id(booking_seat_id)

        if not booking_seat:
            raise NotFoundException(description='BookingSeat not found')

        cls._booking_seat = booking_seat
        return booking_seat_id
