import random

import sqlalchemy as sa

from app.models import Booking, BookingSeat, Customer, Discount, Seat, Showtime
from app.models.booking import BookingStatus

from ..factories.booking_factory import BookingFactory, BookingSeatFactory
from . import seed_actions
from .core import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='BookingSeeder', priority=5, factory=BookingFactory)
        self._booking_seat_factory = BookingSeatFactory
        self._session = self.factory.get_db_session()

    def _create_booking_seat(self, booking: Booking, showtime: Showtime) -> None:
        booked_booking_ids_subquery = [b.id for b in showtime.bookings if booking.status == BookingStatus.CONFIRMED]
        available_seat = self._session.query(Seat).order_by(sa.func.random()).first()

        if booked_booking_ids_subquery:
            seat_ids_subquery = (
                self._session.query(BookingSeat)
                .with_entities(BookingSeat.seat_id)
                .filter(~BookingSeat.booking_id.in_(booked_booking_ids_subquery))
            )

            if len(booked_booking_ids_subquery):
                available_seat = (
                    self._session.query(Seat)
                    .filter(~Seat.id.notin_(seat_ids_subquery))
                    .order_by(sa.func.random())
                    .first()
                )

        self._booking_seat_factory.create(
            booking=booking,
            seat=available_seat,
        )

    def _create_booking(self, customer: Customer, discounts: list[Discount], showtimes: list[Showtime]) -> None:
        if random.choice([True, False]):
            for _ in range(0, 3):
                # NOTE: There is a problem on the factory creation when a `Customer` model is sent.
                #       So if `Customer.id` is sent instead of `Customer` then it works.
                kwargs = {'customer_id': customer.id, 'showtime': random.choice(showtimes), 'discount': None}

                if random.choice([True, False]):
                    kwargs['discount'] = random.choice(discounts)

                self._create_booking_seat(booking=self.factory.create(**kwargs), showtime=kwargs['showtime'])

    @seed_actions
    def seed(self, rows: int = None) -> None:
        customers = self._session.query(Customer).all()
        showtimes = self._session.query(Showtime).all()
        discounts = self._session.query(Discount).all()

        for customer in customers:
            self._create_booking(customer, discounts, showtimes)
