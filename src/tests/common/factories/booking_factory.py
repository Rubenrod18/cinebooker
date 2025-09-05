from datetime import timedelta
from decimal import Decimal

import factory

from app.models import Booking
from app.models.booking import BookingSeat, BookingStatus
from tests.common.factories.base_factory import BaseFactory
from tests.common.factories.customer_factory import CustomerFactory
from tests.common.factories.discount_factory import DiscountFactory
from tests.common.factories.seat_factory import SeatFactory
from tests.common.factories.showtime_factory import ShowtimeFactory


class BookingFactory(BaseFactory):
    class Meta:
        model = Booking

    customer = factory.SubFactory(CustomerFactory)
    showtime = factory.SubFactory(ShowtimeFactory)
    discount = factory.Iterator([factory.SubFactory(DiscountFactory), None])

    status = factory.Iterator(BookingStatus.to_list())
    created_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    updated_at = factory.Faker('date_time_between', start_date='-1y', end_date='now')

    @factory.lazy_attribute
    def expired_at(self):
        expired_at = None

        if self.status == BookingStatus.EXPIRED:
            expired_at = self.created_at + timedelta(minutes=5)

        return expired_at


class BookingSeatFactory(BaseFactory):
    class Meta:
        model = BookingSeat

    booking = factory.Sequence(BookingFactory)
    seat = factory.SubFactory(SeatFactory)

    base_price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
    vat_rate = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)

    @factory.lazy_attribute
    def price_with_vat(self):
        return (self.base_price * (1 + self.vat_rate)).quantize(Decimal('0.01'))
