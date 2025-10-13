import random
import uuid
from datetime import timedelta

import factory

from app.models import Discount

from ...conftest import fake
from .base_factory import BaseFactory


class DiscountFactory(BaseFactory):
    class Meta:
        model = Discount

    code = factory.Sequence(lambda n: f'Discount_code_{n}_{uuid.uuid4().hex}')
    description = factory.Sequence(lambda n: f'Discount description {n}')
    is_percentage = factory.Sequence(lambda n: True if n % 10 == 0 else False)
    amount = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=5, max_value=30)
    usages_limit = factory.Iterator([fake.random_int(min=1, max=10), None])
    created_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    updated_at = factory.Faker('date_time_between', start_date='-1y', end_date='now')

    @factory.lazy_attribute
    def expired_at(self):
        expiration_time = timedelta(days=30)
        return random.choice([self.created_at + expiration_time, None])

    @factory.lazy_attribute
    def times_used(self):
        times_used = None

        if self.usages_limit:
            times_used = fake.random_int(min=0, max=self.usages_limit)

        return times_used

    @factory.lazy_attribute
    def inactive_at(self):
        return random.choice([self.created_at + timedelta(days=7), None])


class EnabledDiscountFactory(DiscountFactory):
    inactive_at = None


class DisabledDiscountFactory(DiscountFactory):
    @factory.lazy_attribute
    def inactive_at(self):
        return self.created_at + timedelta(days=2)


class ExpiredDiscountFactory(DiscountFactory):
    @factory.lazy_attribute
    def expired_at(self):
        expiration_time = timedelta(days=30)
        return self.created_at + expiration_time
