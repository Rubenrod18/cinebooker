from sqlmodel import Session, SQLModel

from app.models import Screen
from app.repositories.screen_repository import ScreenRepository
from app.services import core


class ScreenService(
    core.AbstractCreateService,
    core.FindByIdMixin,
    core.GetMixin,
    core.AbstractUpdateService,
    core.AbstractDeleteService,
):
    def __init__(
        self,
        session: type[Session] = None,
        customer_repository: ScreenRepository | None = None,
    ):
        super().__init__(repository=customer_repository or ScreenRepository(session))

    def create(self, **kwargs) -> Screen:
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> Screen:
        return self.repository.update(record, **kwargs)

    def delete(self, record, **kwargs) -> SQLModel | None:
        return self.repository.delete(record, **kwargs)
