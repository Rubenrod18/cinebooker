from datetime import date

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from ..utils.constants import BaseEnum
from .core import IntegerPKMixin


class MovieGenre(BaseEnum):
    ACTION = 'action'
    COMEDY = 'comedy'
    DRAMA = 'drama'
    HORROR = 'horror'
    ROMANCE = 'romance'
    SCIENCE_FICTION = 'science_fiction'
    THRILLER = 'thriller'
    ANIMATION = 'animation'
    DOCUMENTARY = 'documentary'
    FANTASY = 'fantasy'


class Movie(IntegerPKMixin, SQLModel, table=True):
    _tablename__ = 'movie'

    title: str
    description: str
    duration: int
    release_date: date
    genre: MovieGenre = Field(
        sa_column=sa.Column(
            sa.Enum(
                MovieGenre,
                name='moviegenre',
                values_callable=lambda enum: [e.value for e in enum],
                create_type=True,
            ),
            nullable=False,
        )
    )
    director: str
    language: str

    showtimes: list['Showtime'] | None = Relationship(back_populates='movie')
