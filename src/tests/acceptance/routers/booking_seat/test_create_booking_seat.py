import uuid
from datetime import datetime
from unittest.mock import ANY, MagicMock

import pytest
from redis import Redis

from app.models import BookingSeat, Ticket
from app.models.ticket import TicketStatus
from app.utils import financials
from tests.acceptance.routers.booking_seat._base_booking_seats_test import _TestBaseBookingSeatEndpoints
from tests.common.factories.booking_factory import (
    CancelledBookingFactory,
    ConfirmedBookingFactory,
    ConfirmedBookingSeatFactory,
    ExpiredBookingFactory,
    PendingPaymentBookingFactory,
)
from tests.common.factories.seat_factory import EnabledSeatFactory


class TestCreateBookingSeatEndpoint(_TestBaseBookingSeatEndpoints):
    def test_field_prices_have_invalid_format(self):
        booking = PendingPaymentBookingFactory()
        seat = EnabledSeatFactory()
        payload = {
            'booking_id': str(booking.id),
            'seat_id': seat.id,
            'base_price': self.faker.random_letter(),
            'vat_rate': self.faker.random_letter(),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'type': 'decimal_parsing',
                    'loc': ['body', 'base_price'],
                    'msg': 'Input should be a valid decimal',
                    'input': payload['base_price'],
                },
                {
                    'type': 'decimal_parsing',
                    'loc': ['body', 'vat_rate'],
                    'msg': 'Input should be a valid decimal',
                    'input': payload['vat_rate'],
                },
            ]
        }

    def test_base_price_less_than_one(self):
        booking = PendingPaymentBookingFactory()
        seat = EnabledSeatFactory()
        payload = {
            'booking_id': str(booking.id),
            'seat_id': seat.id,
            'base_price': 0,
            'vat_rate': str(
                self.faker.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)
            ),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'ctx': {
                        'ge': 1,
                    },
                    'type': 'greater_than_equal',
                    'loc': ['body', 'base_price'],
                    'msg': 'Input should be greater than or equal to 1',
                    'input': payload['base_price'],
                },
            ]
        }

    def test_vat_rate_less_than_zero(self):
        booking = PendingPaymentBookingFactory()
        seat = EnabledSeatFactory()
        payload = {
            'booking_id': str(booking.id),
            'seat_id': seat.id,
            'base_price': str(
                self.faker.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
            ),
            'vat_rate': -1,
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'ctx': {
                        'gt': 0,
                    },
                    'type': 'greater_than',
                    'loc': ['body', 'vat_rate'],
                    'msg': 'Input should be greater than 0',
                    'input': payload['vat_rate'],
                },
            ]
        }

    def test_booking_not_found(self):
        seat = EnabledSeatFactory()
        payload = {
            'booking_id': str(uuid.uuid4()),
            'seat_id': seat.id,
            'base_price': str(
                self.faker.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
            ),
            'vat_rate': str(
                self.faker.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)
            ),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Booking not found'}

    def test_seat_not_found(self):
        booking = PendingPaymentBookingFactory()
        payload = {
            'booking_id': str(booking.id),
            'seat_id': 99,
            'base_price': str(
                self.faker.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
            ),
            'vat_rate': str(
                self.faker.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)
            ),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Seat not found'}

    @pytest.mark.parametrize(
        'booking_factory',
        [ConfirmedBookingFactory, CancelledBookingFactory, ExpiredBookingFactory],
        ids=['confirmed', 'cancelled', 'expired'],
    )
    def test_create_invalid_booking(self, booking_factory):
        booking = booking_factory()
        seat = EnabledSeatFactory()
        payload = {
            'booking_id': str(booking.id),
            'seat_id': seat.id,
            'base_price': str(
                self.faker.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
            ),
            'vat_rate': str(
                self.faker.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)
            ),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Booking not found'}

    def test_create_seat_not_available(self):
        booking_seat = ConfirmedBookingSeatFactory()
        booking = PendingPaymentBookingFactory(showtime=booking_seat.booking.showtime)

        payload = {
            'booking_id': str(booking.id),
            'seat_id': booking_seat.seat.id,
            'base_price': str(
                self.faker.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
            ),
            'vat_rate': str(
                self.faker.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)
            ),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {'detail': 'Seat is not available'}

    def test_create_seat_not_available_with_redis(self):
        mock_redis_client = MagicMock(spec=Redis)
        mock_redis_client.exists.return_value = True

        booking_seat = ConfirmedBookingSeatFactory()
        booking = PendingPaymentBookingFactory(showtime=booking_seat.booking.showtime)

        payload = {
            'booking_id': str(booking.id),
            'seat_id': booking_seat.seat.id,
            'base_price': str(
                self.faker.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
            ),
            'vat_rate': str(
                self.faker.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)
            ),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {'detail': 'Seat is not available'}

    def test_create_booking_seat(self):
        mock_redis_client = MagicMock(spec=Redis)
        mock_redis_client.exists.return_value = False

        booking = PendingPaymentBookingFactory()
        seat = EnabledSeatFactory()

        payload = {
            'booking_id': str(booking.id),
            'seat_id': seat.id,
            'base_price': str(
                self.faker.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
            ),
            'vat_rate': str(
                self.faker.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)
            ),
        }

        with self.app.container.redis_client.override(mock_redis_client):
            response = self.client.post(url=self.base_path, json=payload)

            expected_price_with_vat = str(financials.apply_vat_rate(payload['base_price'], payload['vat_rate']))
            assert response.json() == {
                'base_price': str(payload['base_price']),
                'booking_id': payload['booking_id'],
                'created_at': ANY,
                'id': 1,
                'price_with_vat': expected_price_with_vat,
                'seat_id': payload['seat_id'],
                'updated_at': ANY,
                'vat_rate': payload['vat_rate'],
            }

            mock_redis_client.set.assert_called_once_with(
                name=f'booking_seat:{booking.showtime_id}_{seat.id}', value='locked', ex=300
            )

        with self.app.container.session() as session:
            booking_seat = session.query(BookingSeat).first()
            assert booking_seat
            assert str(booking_seat.booking_id) == payload['booking_id']
            assert booking_seat.seat_id == payload['seat_id']
            assert str(booking_seat.base_price) == payload['base_price']
            assert str(booking_seat.vat_rate) == payload['vat_rate']
            assert str(booking_seat.price_with_vat) == expected_price_with_vat

            ticket = session.query(Ticket).first()
            assert ticket
            assert ticket.booking_seat_id == booking_seat.id
            assert len(ticket.barcode_value) == 30
            assert ticket.status == TicketStatus.ISSUED
            assert isinstance(ticket.issued_at, datetime)
            assert ticket.redeemed_at is None
