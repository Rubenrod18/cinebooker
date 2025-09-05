import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from .core import CreatedUpdatedMixin, InactiveMixin, IntegerPKMixin


class Seat(IntegerPKMixin, CreatedUpdatedMixin, InactiveMixin, SQLModel, table=True):
    __tablename__ = 'seat'

    screen_id: int = Field(foreign_key='screen.id')
    screen: 'Screen' = Relationship(back_populates='seats', sa_relationship_kwargs={'uselist': False})

    number: int
    row: int

    booking_seat: list['BookingSeat'] | None = Relationship(back_populates='seat')

    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('screen_id', 'number', 'row'),
    )
