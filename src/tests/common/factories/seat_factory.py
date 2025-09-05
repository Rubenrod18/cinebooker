import random
from datetime import timedelta

import factory

from app.models import Seat
from tests.common.factories.base_factory import BaseFactory
from tests.common.factories.screen_factory import ScreenFactory


class SeatFactory(BaseFactory):
    class Meta:
        model = Seat

    screen = factory.SubFactory(ScreenFactory)

    number = factory.Sequence(lambda n: n + 1)
    row = factory.Sequence(lambda n: n + 1)
    created_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    updated_at = factory.Faker('date_time_between', start_date='-1y', end_date='now')

    @factory.lazy_attribute
    def inactive_at(self):
        return random.choice([self.created_at + timedelta(days=2), None])
