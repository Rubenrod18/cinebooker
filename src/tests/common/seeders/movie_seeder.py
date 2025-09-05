from ..factories.movie_factory import MovieFactory
from . import seed_actions
from .core import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='MovieSeeder', priority=1, factory=MovieFactory)
        self._default_rows = 10

    @seed_actions
    def seed(self, rows: int = None) -> None:
        self.factory.create_batch(rows or self._default_rows)
