from unittest.mock import ANY

from app.utils import financials
from tests.acceptance.routers.booking_seat._base_booking_seats_test import _TestBaseBookingSeatEndpoints
from tests.common.factories.booking_factory import ConfirmedBookingSeatFactory


class TestGetBookingSeatRouter(_TestBaseBookingSeatEndpoints):
    def test_not_found(self):
        response = self.client.get(url=f'{self.base_path}/99', json={}, exp_code=404)

        assert response.json() == {'detail': 'BookingSeat not found'}

    def test_find_by_id_enabled_booking_seat(self):
        booking_seat = ConfirmedBookingSeatFactory()

        response = self.client.get(url=f'{self.base_path}/{booking_seat.id}', json={})

        assert response.json() == {
            'base_price': str(booking_seat.base_price),
            'booking_id': str(booking_seat.booking.id),
            'created_at': ANY,
            'id': 1,
            'price_with_vat': str(financials.apply_vat_rate(booking_seat.base_price, booking_seat.vat_rate)),
            'seat_id': booking_seat.seat.id,
            'updated_at': ANY,
            'vat_rate': str(booking_seat.vat_rate),
        }
