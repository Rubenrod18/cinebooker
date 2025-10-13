from sqlmodel import Session

from app.models import Showtime
from app.repositories.showtime_repository import ShowtimeRepository
from app.services import core


class ShowtimeService(
    core.AbstractCreateService,
    core.FindByIdMixin,
    core.GetMixin,
    core.AbstractUpdateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        showtime_repository: ShowtimeRepository | None = None,
    ):
        super().__init__(repository=showtime_repository or ShowtimeRepository(session))

    def create(self, **kwargs) -> Showtime:
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> Showtime:
        return self.repository.update(record, **kwargs)
