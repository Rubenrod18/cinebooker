from decimal import Decimal

import factory

from app.models import Showtime
from tests.common.factories.base_factory import BaseFactory
from tests.common.factories.movie_factory import MovieFactory
from tests.common.factories.screen_factory import ScreenFactory


class ShowtimeFactory(BaseFactory):
    class Meta:
        model = Showtime

    movie = factory.SubFactory(MovieFactory)
    screen = factory.SubFactory(ScreenFactory)

    start_time = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    base_price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
    vat_rate = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)

    @factory.lazy_attribute
    def price_with_vat(self):
        return (self.base_price * (1 + self.vat_rate)).quantize(Decimal('0.01'))
