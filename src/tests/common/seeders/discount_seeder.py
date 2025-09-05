from ..factories.discount_factory import DiscountFactory
from . import seed_actions
from .core import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='DiscountSeeder', priority=4, factory=DiscountFactory)
        self._default_rows = 6

    @seed_actions
    def seed(self, rows: int = None) -> None:
        self.factory.create_batch(rows or self._default_rows)
