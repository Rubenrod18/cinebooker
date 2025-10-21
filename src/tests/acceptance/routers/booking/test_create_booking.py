import uuid
from unittest.mock import ANY

from app.models.booking import Booking, BookingStatus
from tests.acceptance.routers.booking._base_booking_test import _TestBaseBookingEndpoints
from tests.common.factories.customer_factory import EnabledCustomerFactory
from tests.common.factories.discount_factory import EnabledDiscountFactory
from tests.common.factories.showtime_factory import EnabledShowtimeFactory


class TestCreateBookingEndpoint(_TestBaseBookingEndpoints):
    def test_customer_not_found(self):
        showtime = EnabledShowtimeFactory()
        payload = {'customer_id': 99, 'showtime_id': str(showtime.id)}

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Customer not found'}

    def test_showtime_not_found(self):
        customer = EnabledCustomerFactory()
        payload = {'customer_id': customer.id, 'showtime_id': str(uuid.uuid4())}

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Showtime not found'}

    def test_discount_not_found(self):
        customer = EnabledCustomerFactory()
        showtime = EnabledShowtimeFactory()
        payload = {'customer_id': customer.id, 'showtime_id': str(showtime.id), 'discount_code': 'fake-discount-code'}

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Discount not found'}

    def test_create_booking_with_discount(self):
        customer = EnabledCustomerFactory()
        showtime = EnabledShowtimeFactory()
        discount = EnabledDiscountFactory()
        payload = {'customer_id': customer.id, 'showtime_id': str(showtime.id), 'discount_code': discount.code}

        response = self.client.post(url=self.base_path, json=payload)
        json_response = response.json()

        assert json_response['customer_id'] == payload['customer_id']
        assert json_response['showtime_id'] == payload['showtime_id']
        assert json_response['discount_id'] == discount.id
        assert json_response['status'] == BookingStatus.PENDING_PAYMENT.value
        assert json_response['expired_at'] is None

        with self.app.container.session() as session:
            booking = session.query(Booking).first()
            assert booking
            assert isinstance(booking.id, uuid.UUID)
            assert booking.customer_id == payload['customer_id']
            assert str(booking.showtime_id) == payload['showtime_id']
            assert booking.discount_id == discount.id
            assert booking.status == BookingStatus.PENDING_PAYMENT.value
            assert booking.expired_at is None
            assert booking.created_at == ANY
            assert booking.updated_at == ANY

    def test_create_booking_without_discount(self):
        customer = EnabledCustomerFactory()
        showtime = EnabledShowtimeFactory()
        payload = {'customer_id': customer.id, 'showtime_id': str(showtime.id)}

        response = self.client.post(url=self.base_path, json=payload)
        json_response = response.json()

        assert json_response['customer_id'] == payload['customer_id']
        assert json_response['showtime_id'] == payload['showtime_id']
        assert json_response['discount_id'] is None
        assert json_response['status'] == BookingStatus.PENDING_PAYMENT.value
        assert json_response['expired_at'] is None

        with self.app.container.session() as session:
            booking = session.query(Booking).first()
            assert booking
            assert isinstance(booking.id, uuid.UUID)
            assert booking.customer_id == payload['customer_id']
            assert str(booking.showtime_id) == payload['showtime_id']
            assert booking.discount_id is None
            assert booking.status == BookingStatus.PENDING_PAYMENT.value
            assert booking.expired_at is None
            assert booking.created_at == ANY
            assert booking.updated_at == ANY
