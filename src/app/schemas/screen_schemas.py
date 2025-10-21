from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, ConfigDict, Field, field_validator, PrivateAttr

from ..di_container import ServiceDIContainer
from ..exceptions import NotFoundException
from ..models import Screen
from ..repositories.screen_repository import ScreenRepository
from . import core


class ScreenCreateSchema(BaseModel):
    name: str
    capacity: int = Field(..., ge=1)


class ScreenUpdateSchema(BaseModel):
    name: str | None = None
    capacity: int | None = Field(None, ge=1)


class ScreenResponseSchema(core.IntegerPKMixin, core.CreatedUpdatedMixin, core.InactiveMixin, BaseModel):
    name: str
    capacity: int

    model_config = ConfigDict(from_attributes=True)


class ScreenIdRequestSchema(BaseModel):
    screen_id: int
    _screen: Screen | None = PrivateAttr(default=None)

    @field_validator('screen_id')
    @classmethod
    @inject
    def validate_screen_id(
        cls, screen_id: int, screen_repository: ScreenRepository = Provide[ServiceDIContainer.screen_repository]
    ) -> int:
        screen = screen_repository.find_by_id(screen_id)

        if not screen:
            raise NotFoundException(description='Screen not found')

        cls._screen = screen
        return screen_id

    @property
    def screen(self) -> Screen:
        return self._screen
