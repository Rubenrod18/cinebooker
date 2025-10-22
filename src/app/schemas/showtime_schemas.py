from datetime import datetime
from decimal import Decimal
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, ConfigDict, Field, field_validator, FutureDatetime, model_validator, PrivateAttr

from ..di_container import ServiceDIContainer
from ..exceptions import NotFoundException, UnprocessableEntityException
from ..models import Showtime
from ..repositories.movie_repository import MovieRepository
from ..repositories.screen_repository import ScreenRepository
from ..repositories.showtime_repository import ShowtimeRepository
from ..utils import financials
from . import core


class ShowtimeCreateSchema(BaseModel):
    movie_id: int
    screen_id: int
    start_time: FutureDatetime
    base_price: Decimal = Field(..., ge=1)
    vat_rate: Decimal = Field(..., gt=0)
    price_with_vat: Decimal = Field(..., ge=1)

    @field_validator('movie_id')
    @classmethod
    @inject
    def validate_movie_id(
        cls, movie_id: int, movie_repository: MovieRepository = Provide[ServiceDIContainer.movie_repository]
    ) -> int:
        if not movie_repository.find_by_id(movie_id):
            raise NotFoundException(description='Movie not found')

        return movie_id

    @field_validator('screen_id')
    @classmethod
    @inject
    def validate_screen_id(
        cls, screen_id: int, screen_repository: ScreenRepository = Provide[ServiceDIContainer.screen_repository]
    ) -> int:
        if not screen_repository.find_by_id(screen_id):
            raise NotFoundException(description='Screen not found')

        return screen_id

    @model_validator(mode='after')
    def validate_price_with_vat(self):
        # NOTE: This logic must be done by the backend
        if self.price_with_vat != financials.apply_vat_rate(self.base_price, self.vat_rate):
            raise UnprocessableEntityException(description='price_with_vat does not match base_price and vat_rate')

        return self


class ShowtimeUpdateSchema(BaseModel):
    movie_id: int | None = None
    screen_id: int | None = None
    start_time: FutureDatetime | None = None
    base_price: Decimal | None = Field(None, ge=1)
    vat_rate: Decimal | None = Field(None, gt=0)
    price_with_vat: Decimal | None = Field(None, ge=1)

    @field_validator('movie_id')
    @classmethod
    @inject
    def validate_movie_id(
        cls, movie_id: int | None, movie_repository: MovieRepository = Provide[ServiceDIContainer.movie_repository]
    ) -> int | None:
        if movie_id and not movie_repository.find_by_id(movie_id):
            raise NotFoundException(description='Movie not found')

        return movie_id

    @field_validator('screen_id')
    @classmethod
    @inject
    def validate_screen_id(
        cls, screen_id: int | None, screen_repository: ScreenRepository = Provide[ServiceDIContainer.screen_repository]
    ) -> int | None:
        if screen_id and not screen_repository.find_by_id(screen_id):
            raise NotFoundException(description='Screen not found')

        return screen_id


class ShowtimeResponseSchema(core.UUIDPKMixin, core.CreatedUpdatedMixin, BaseModel):
    movie_id: int
    screen_id: int
    start_time: datetime
    base_price: Decimal
    vat_rate: Decimal
    price_with_vat: Decimal

    model_config = ConfigDict(from_attributes=True)


class ShowtimeIdRequestSchema(BaseModel):
    showtime_id: UUID
    _showtime: Showtime | None = PrivateAttr(default=None)

    @field_validator('showtime_id')
    @classmethod
    @inject
    def validate_showtime_id(
        cls, showtime_id: int, showtime_repository: ShowtimeRepository = Provide[ServiceDIContainer.showtime_repository]
    ) -> int:
        showtime = showtime_repository.find_by_id(showtime_id)

        if not showtime:
            raise NotFoundException(description='Showtime not found')

        cls._showtime = showtime
        return showtime_id

    @property
    def showtime(self) -> Showtime:
        return self._showtime
