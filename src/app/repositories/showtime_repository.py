from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from app.models import Showtime
from app.repositories import core


class ShowtimeRepository(
    core.AbstractCreateRepository,
    core.FindByIdMixin,
    core.GetMixin,
    core.AbstractUpdateRepository,
):
    def __init__(self, session: Session):
        super().__init__(model=Showtime, session=session)

    def create(self, **kwargs) -> Showtime:
        showtime = self.model(**kwargs)
        self.session.add(showtime)
        self.session.flush()
        return showtime

    def update(self, record, **kwargs) -> SQLModel | None:
        for field, value in kwargs.items():
            setattr(record, field, value)

        return record
