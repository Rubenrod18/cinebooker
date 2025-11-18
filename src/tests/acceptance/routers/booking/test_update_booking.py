import uuid
from unittest.mock import ANY

from app.models import Booking, InvoiceItem
from app.models.booking import BookingStatus
from tests.acceptance.routers.booking._base_booking_test import _TestBaseBookingEndpoints
from tests.common.factories.booking_factory import EnabledBookingFactory
from tests.common.factories.customer_factory import EnabledCustomerFactory
from tests.common.factories.discount_factory import EnabledDiscountFactory
from tests.common.factories.invoice_factory import InvoiceItemFactory, IssuedInvoiceFactory
from tests.common.factories.showtime_factory import EnabledShowtimeFactory


class TestUpdateShowtimeRouter(_TestBaseBookingEndpoints):
    def test_not_found(self):
        response = self.client.patch(url=f'{self.base_path}/{uuid.uuid4()}', json={}, exp_code=404)
        json_response = response.json()

        assert json_response
        assert json_response == {'detail': 'Booking not found'}

    def test_customer_not_found(self):
        booking = EnabledBookingFactory(status=BookingStatus.PENDING_PAYMENT.value)
        payload = {'customer_id': 99}

        response = self.client.patch(url=f'{self.base_path}/{booking.id}', json=payload, exp_code=404)

        assert response.json() == {'detail': 'Customer not found'}

    def test_showtime_not_found(self):
        booking = EnabledBookingFactory(status=BookingStatus.PENDING_PAYMENT.value)
        payload = {'showtime_id': str(uuid.uuid4())}

        response = self.client.patch(url=f'{self.base_path}/{booking.id}', json=payload, exp_code=404)

        assert response.json() == {'detail': 'Showtime not found'}

    def test_discount_not_found(self):
        booking = EnabledBookingFactory(status=BookingStatus.PENDING_PAYMENT.value)
        payload = {'discount_code': 'fake-discount-code'}

        response = self.client.patch(url=f'{self.base_path}/{booking.id}', json=payload, exp_code=404)

        assert response.json() == {'detail': 'Discount not found'}

    def test_no_update_fields(self):
        booking = EnabledBookingFactory(status=BookingStatus.PENDING_PAYMENT.value, discount=None)
        payload = {}

        response = self.client.patch(url=f'{self.base_path}/{booking.id}', json=payload)
        json_response = response.json()

        assert json_response['customer_id'] == booking.customer.id
        assert json_response['showtime_id'] == str(booking.showtime.id)
        assert json_response['discount_id'] is None
        assert json_response['status'] == BookingStatus.PENDING_PAYMENT.value
        assert json_response['expired_at'] is None

        with self.app.container.session() as session:
            booking = session.query(Booking).first()
            assert booking
            assert isinstance(booking.id, uuid.UUID)
            assert booking.customer_id == booking.customer.id
            assert str(booking.showtime_id) == str(booking.showtime.id)
            assert booking.discount_id is None
            assert booking.status == BookingStatus.PENDING_PAYMENT.value
            assert booking.expired_at is None
            assert booking.created_at == ANY
            assert booking.updated_at == ANY

    def test_update_booking_with_discount(self):
        current_booking = EnabledBookingFactory(
            status=BookingStatus.PENDING_PAYMENT.value, discount=EnabledDiscountFactory()
        )
        customer = EnabledCustomerFactory()
        showtime = EnabledShowtimeFactory()
        discount = EnabledDiscountFactory()
        payload = {'customer_id': customer.id, 'showtime_id': str(showtime.id), 'discount_code': discount.code}

        response = self.client.patch(url=f'{self.base_path}/{current_booking.id}', json=payload)
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
            assert booking.id == current_booking.id
            assert booking.customer_id == payload['customer_id']
            assert str(booking.showtime_id) == payload['showtime_id']
            assert booking.discount_id == discount.id
            assert booking.status == BookingStatus.PENDING_PAYMENT.value
            assert booking.expired_at is None
            assert booking.created_at == ANY
            assert booking.updated_at == ANY

    def test_update_booking_without_discount(self):
        booking = EnabledBookingFactory(status=BookingStatus.PENDING_PAYMENT.value, discount=None)
        customer = EnabledCustomerFactory()
        showtime = EnabledShowtimeFactory()
        payload = {'customer_id': customer.id, 'showtime_id': str(showtime.id)}

        response = self.client.patch(url=f'{self.base_path}/{booking.id}', json=payload)
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

    def test_update_booking_remove_discount(self):
        discount = EnabledDiscountFactory()
        booking = EnabledBookingFactory(status=BookingStatus.PENDING_PAYMENT.value, discount=discount)
        customer = EnabledCustomerFactory()
        showtime = EnabledShowtimeFactory()
        invoice = IssuedInvoiceFactory(booking=booking)
        InvoiceItemFactory(booking=booking, invoice=invoice, description='Seats')
        InvoiceItemFactory(booking=booking, invoice=invoice, description='Discount code')
        payload = {'customer_id': customer.id, 'showtime_id': str(showtime.id), 'discount_id': None}

        response = self.client.patch(url=f'{self.base_path}/{booking.id}', json=payload)
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

            assert session.query(InvoiceItem).filter(InvoiceItem.description.like('%Discount%')).count() == 0
            assert session.query(InvoiceItem).filter(InvoiceItem.description.like('%Seats%')).count() == 1
