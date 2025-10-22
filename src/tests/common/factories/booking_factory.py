from datetime import timedelta

import factory

from app.models import Booking
from app.models.booking import BookingSeat, BookingStatus
from app.utils import financials
from tests.common.factories.base_factory import BaseFactory
from tests.common.factories.customer_factory import CustomerFactory, EnabledCustomerFactory
from tests.common.factories.discount_factory import DiscountFactory, EnabledDiscountFactory
from tests.common.factories.seat_factory import EnabledSeatFactory, SeatFactory
from tests.common.factories.showtime_factory import EnabledShowtimeFactory, ShowtimeFactory


class BookingFactory(BaseFactory):
    class Meta:
        model = Booking

    customer = factory.SubFactory(CustomerFactory)
    showtime = factory.SubFactory(ShowtimeFactory)
    discount = factory.Maybe(
        'has_discount',
        yes_declaration=factory.SubFactory(DiscountFactory),
        no_declaration=None,
    )

    status = factory.Iterator(BookingStatus.to_list())
    created_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    updated_at = factory.Faker('date_time_between', start_date='-1y', end_date='now')

    @factory.lazy_attribute
    def expired_at(self):
        expired_at = None

        if self.status == BookingStatus.EXPIRED:
            expired_at = self.created_at + timedelta(minutes=5)

        return expired_at


class EnabledBookingFactory(BookingFactory):
    customer = factory.SubFactory(EnabledCustomerFactory)
    showtime = factory.SubFactory(EnabledShowtimeFactory)
    discount = factory.Maybe(
        'has_discount',
        yes_declaration=factory.SubFactory(EnabledDiscountFactory),
        no_declaration=None,
    )
    status = factory.Iterator([BookingStatus.PENDING_PAYMENT.value, BookingStatus.CONFIRMED.value])


class PendingPaymentBookingFactory(EnabledBookingFactory):
    status = BookingStatus.PENDING_PAYMENT.value


class ConfirmedBookingFactory(EnabledBookingFactory):
    status = BookingStatus.CONFIRMED.value


class CancelledBookingFactory(EnabledBookingFactory):
    status = BookingStatus.CANCELLED.value


class ExpiredBookingFactory(EnabledBookingFactory):
    status = BookingStatus.EXPIRED.value


class BookingSeatFactory(BaseFactory):
    class Meta:
        model = BookingSeat

    booking = factory.Sequence(BookingFactory)
    seat = factory.SubFactory(SeatFactory)

    base_price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
    vat_rate = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)

    @factory.lazy_attribute
    def price_with_vat(self):
        return financials.apply_vat_rate(self.base_price, self.vat_rate)


class PendingPaymentBookingSeatFactory(BookingSeatFactory):
    booking = factory.SubFactory(PendingPaymentBookingFactory)
    seat = factory.SubFactory(EnabledSeatFactory)


class ConfirmedBookingSeatFactory(BookingSeatFactory):
    booking = factory.SubFactory(ConfirmedBookingFactory)
    seat = factory.SubFactory(EnabledSeatFactory)


class ExpiredBookingSeatFactory(BookingSeatFactory):
    booking = factory.SubFactory(ExpiredBookingFactory)
    seat = factory.SubFactory(EnabledSeatFactory)


class CancelledBookingSeatFactory(BookingSeatFactory):
    booking = factory.SubFactory(CancelledBookingFactory)
    seat = factory.SubFactory(EnabledSeatFactory)
