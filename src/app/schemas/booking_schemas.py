from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, ConfigDict, Field, field_validator, PrivateAttr

from ..di_container import ServiceDIContainer
from ..exceptions import NotFoundException
from ..models import Booking
from ..models.booking import BookingStatus
from ..repositories.booking_repository import BookingRepository
from ..repositories.customer_repository import CustomerRepository
from ..repositories.showtime_repository import ShowtimeRepository
from . import core
from .customer_schemas import CustomerIdRequestSchema
from .discount_schemas import DiscountCodeRequestSchema
from .showtime_schemas import ShowtimeIdRequestSchema


class BookingCreateSchema(
    CustomerIdRequestSchema,
    ShowtimeIdRequestSchema,
    DiscountCodeRequestSchema,
):
    discount_code: str | None = None
    discount_id: int | None = Field(default=None, alias='discount_code')

    @field_validator('discount_id', mode='before')
    @classmethod
    @inject
    def validate_discount_id(
        cls,
        discount_code: str | None,
    ) -> str:
        return cls._discount.id if discount_code else discount_code


class BookingUpdateSchema(
    CustomerIdRequestSchema,
    ShowtimeIdRequestSchema,
    DiscountCodeRequestSchema,
):
    customer_id: int | None = None
    showtime_id: UUID | None = None
    discount_code: str | None = Field(default=None, exclude=True)
    discount_id: int | None = Field(default=None, alias='discount_code')

    @field_validator('customer_id')
    @classmethod
    @inject
    def validate_customer_id(
        cls, customer_id: int, customer_repository: CustomerRepository = Provide[ServiceDIContainer.customer_repository]
    ) -> int:
        if customer_id:
            return super().validate_customer_id(customer_id)

        return customer_id

    @field_validator('showtime_id')
    @classmethod
    @inject
    def validate_showtime_id(
        cls, showtime_id: int, showtime_repository: ShowtimeRepository = Provide[ServiceDIContainer.showtime_repository]
    ) -> int:
        if showtime_id:
            return super().validate_showtime_id(showtime_id)

        return showtime_id

    @field_validator('discount_id', mode='before')
    @classmethod
    @inject
    def validate_discount_id(
        cls,
        discount_code: str | None,
    ) -> str:
        return cls._discount.id if discount_code else discount_code


class BookingResponseSchema(core.UUIDPKMixin, core.CreatedUpdatedMixin, BaseModel):
    customer_id: int
    showtime_id: UUID
    discount_id: int | None
    status: BookingStatus
    expired_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class BookingIdRequestSchema(BaseModel):
    booking_id: UUID
    _booking: Booking | None = PrivateAttr(default=None)

    @field_validator('booking_id')
    @classmethod
    @inject
    def validate_booking_id(
        cls, booking_id: UUID, booking_repository: BookingRepository = Provide[ServiceDIContainer.booking_repository]
    ) -> UUID:
        booking = booking_repository.find_by_id(booking_id)

        if not booking:
            raise NotFoundException(description='Booking not found')

        cls._booking = booking
        return booking_id

    @property
    def booking(self) -> Booking:
        return self._booking
