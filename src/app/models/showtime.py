from datetime import datetime, timedelta
from decimal import Decimal

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from app.models.movie import Movie

from .core import CreatedUpdatedMixin, UUIDPKMixin


class Showtime(UUIDPKMixin, CreatedUpdatedMixin, SQLModel, table=True):
    __tablename__ = 'showtime'

    movie_id: int = Field(foreign_key='movie.id')
    movie: 'Movie' = Relationship(back_populates='showtimes')

    screen_id: int = Field(foreign_key='screen.id')
    screen: 'Screen' = Relationship(back_populates='showtimes')

    start_time: datetime
    base_price: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    vat_rate: Decimal = Field(sa_column=sa.DECIMAL(12, 2))
    price_with_vat: Decimal = Field(sa_column=sa.DECIMAL(12, 2))

    bookings: list['Booking'] = Relationship(back_populates='showtime')

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.movie.duration)
