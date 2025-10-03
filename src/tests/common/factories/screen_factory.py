import random
from datetime import timedelta

import factory

from app.models import Screen
from tests.common.factories.base_factory import BaseFactory


class ScreenFactory(BaseFactory):
    class Meta:
        model = Screen

    name = factory.Sequence(lambda n: f'Screen name {n}')
    capacity = factory.LazyFunction(
        lambda: random.randrange(70, 201, 2)  # start=50, stop=201, step=2 → only even numbers
    )
    created_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    updated_at = factory.Faker('date_time_between', start_date='-1y', end_date='now')

    @factory.lazy_attribute
    def inactive_at(self):
        return random.choice([self.created_at + timedelta(days=2), None])


class EnabledScreenFactory(ScreenFactory):
    inactive_at = None


class DisabledScreenFactory(ScreenFactory):
    @factory.lazy_attribute
    def inactive_at(self):
        return self.created_at + timedelta(days=2)
