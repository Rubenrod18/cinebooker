from sqlmodel import Relationship, SQLModel

from .core import CreatedUpdatedMixin, InactiveMixin, IntegerPKMixin


class Screen(IntegerPKMixin, CreatedUpdatedMixin, InactiveMixin, SQLModel, table=True):
    __tablename__ = 'screen'

    name: str
    capacity: int

    seats: list['Seat'] = Relationship(back_populates='screen')
    showtimes: list['Showtime'] | None = Relationship(back_populates='screen')
