import uuid

from tests.acceptance.routers.booking._base_booking_test import _TestBaseBookingEndpoints
from tests.common.factories.booking_factory import EnabledBookingFactory, ExpiredBookingFactory


class TestGetBookingRouter(_TestBaseBookingEndpoints):
    def test_not_found(self):
        response = self.client.get(url=f'{self.base_path}/{uuid.uuid4()}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Booking not found'}

    def test_find_by_id_expired_booking(self):
        booking = ExpiredBookingFactory()

        response = self.client.get(url=f'{self.base_path}/{booking.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Booking not found'}

    def test_find_by_id_booking(self):
        booking = EnabledBookingFactory()

        response = self.client.get(url=f'{self.base_path}/{booking.id}', json={})
        json_response = response.json()

        assert json_response
        assert json_response['customer_id'] == booking.customer_id
        assert json_response['showtime_id'] == str(booking.showtime_id)
        assert json_response['discount_id'] == booking.discount_id
        assert json_response['status'] == booking.status
        assert json_response['expired_at'] is None
