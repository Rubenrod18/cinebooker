from sqlmodel import Session, SQLModel

from app.models import Seat
from app.repositories.seat_repository import SeatRepository
from app.services import core


class SeatService(
    core.AbstractCreateService,
    core.FindByIdMixin,
    core.GetMixin,
    core.AbstractUpdateService,
    core.AbstractDeleteService,
):
    def __init__(
        self,
        session: type[Session] = None,
        screen_repository: SeatRepository | None = None,
    ):
        super().__init__(repository=screen_repository or SeatRepository(session))

    def create(self, **kwargs) -> Seat:
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> Seat:
        return self.repository.update(record, **kwargs)

    def delete(self, record, **kwargs) -> SQLModel | None:
        return self.repository.delete(record, **kwargs)
