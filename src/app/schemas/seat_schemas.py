from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, ConfigDict, Field, field_validator, PrivateAttr

from ..di_container import ServiceDIContainer
from ..exceptions import NotFoundException
from ..models import Seat
from ..repositories.screen_repository import ScreenRepository
from ..repositories.seat_repository import SeatRepository
from . import core


class SeatCreateSchema(BaseModel):
    screen_id: int
    number: int = Field(..., ge=1)
    row: int = Field(..., ge=1)

    @field_validator('screen_id')
    @classmethod
    @inject
    def validate_screen_id(
        cls, screen_id: int, screen_repository: ScreenRepository = Provide[ServiceDIContainer.screen_repository]
    ) -> int:
        if not screen_repository.find_by_id(screen_id):
            raise NotFoundException(description='Screen not found')

        return screen_id


class SeatUpdateSchema(BaseModel):
    screen_id: int | None = None
    number: int | None = Field(None, ge=1)
    row: int | None = Field(None, ge=1)

    @field_validator('screen_id')
    @classmethod
    @inject
    def validate_screen_id(
        cls, screen_id: int | None, screen_repository: ScreenRepository = Provide[ServiceDIContainer.screen_repository]
    ) -> int | None:
        if screen_id and not screen_repository.find_by_id(screen_id):
            raise NotFoundException(description='Screen not found')

        return screen_id


class SeatResponseSchema(core.IntegerPKMixin, core.CreatedUpdatedMixin, core.InactiveMixin, BaseModel):
    screen_id: int
    number: int
    row: int

    model_config = ConfigDict(from_attributes=True)


class SeatIdRequestSchema(BaseModel):
    seat_id: int
    _seat: Seat | None = PrivateAttr(default=None)

    @field_validator('seat_id')
    @classmethod
    @inject
    def validate_seat_id(
        cls, seat_id: int, seat_repository: SeatRepository = Provide[ServiceDIContainer.seat_repository]
    ) -> int:
        seat = seat_repository.find_by_id(seat_id)

        if not seat:
            raise NotFoundException(description='Seat not found')

        cls._seat = seat
        return seat_id

    @property
    def seat(self) -> Seat:
        return self._seat
