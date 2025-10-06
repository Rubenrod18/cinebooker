from datetime import date

from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, ConfigDict, field_validator, PrivateAttr

from ..di_container import ServiceDIContainer
from ..exceptions import NotFoundException
from ..models import Movie
from ..models.movie import MovieGenre
from ..repositories.movie_repository import MovieRepository
from . import core


class MovieCreateSchema(BaseModel):
    title: str
    description: str
    duration: int
    release_date: date
    genre: MovieGenre
    director: str
    language: str


class MovieUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    duration: int | None = None
    release_date: date | None = None
    genre: MovieGenre | None = None
    director: str | None = None
    language: str | None = None


class MovieResponseSchema(core.IntegerPKMixin, core.CreatedUpdatedMixin, BaseModel):
    title: str
    description: str
    duration: int
    release_date: date
    genre: MovieGenre
    director: str
    language: str
    showtimes: list[int] | None = None

    model_config = ConfigDict(from_attributes=True)


class MovieIdRequestSchema(BaseModel):
    movie_id: int
    _movie: Movie | None = PrivateAttr(default=None)

    @field_validator('movie_id')
    @classmethod
    @inject
    def validate_movie_id(
        cls, movie_id: int, movie_repository: MovieRepository = Provide[ServiceDIContainer.movie_repository]
    ) -> int:
        movie = movie_repository.find_by_id(movie_id)

        if not movie:
            raise NotFoundException(description='Movie not found')

        cls._movie = movie
        return movie_id

    @property
    def movie(self) -> Movie:
        return self._movie
