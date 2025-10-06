from sqlmodel import Session, SQLModel

from app.models import Movie
from app.repositories.movie_repository import MovieRepository
from app.services import core


class MovieService(
    core.AbstractCreateService,
    core.FindByIdMixin,
    core.GetMixin,
    core.AbstractUpdateService,
    core.AbstractDeleteService,
):
    def __init__(
        self,
        session: type[Session] = None,
        movie_repository: MovieRepository | None = None,
    ):
        super().__init__(repository=movie_repository or MovieRepository(session))

    def create(self, **kwargs) -> Movie:
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> Movie:
        return self.repository.update(record, **kwargs)

    def delete(self, record, **kwargs) -> SQLModel | None:
        return self.repository.delete(record, **kwargs)
