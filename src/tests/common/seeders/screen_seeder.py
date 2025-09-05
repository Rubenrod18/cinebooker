from ..factories.screen_factory import ScreenFactory
from ..factories.seat_factory import SeatFactory
from . import seed_actions
from .core import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='ScreenSeeder', priority=2, factory=ScreenFactory)
        self._seat_factory = SeatFactory
        self._default_rows = 6

    @seed_actions
    def seed(self, rows: int = None) -> None:
        screens = [self.factory.create() for _ in range(rows or self._default_rows)]

        for screen in screens:
            for seat_number in range(1, screen.capacity + 1):
                self._seat_factory.create(
                    row=((seat_number - 1) // 10) + 1,  # NOTE: Number of rows
                    number=((seat_number - 1) % 10) + 1,  # NOTE: Seat number in row
                    screen=screen,
                )
