from tests.common.factories.customer_factory import CustomerFactory

from . import seed_actions
from .core import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='CustomerSeeder', priority=0, factory=CustomerFactory)
        self._default_rows = 50

    @seed_actions
    def seed(self, rows: int = None) -> None:
        self.factory.create_batch(rows or self._default_rows)
