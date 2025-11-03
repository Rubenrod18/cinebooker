import uuid
from unittest.mock import ANY, MagicMock

import pytest

from app.models.payment import Payment, PaymentProvider
from app.providers.paypal_provider import PayPalIntent, PayPalOrderStatus, PayPalProvider
from app.services.booking_service import BookingService
from app.services.payment_service import PaymentService
from tests.acceptance.routers.paypal._base_paypal_test import _TestBasePayPalEndpoints
from tests.common.factories.booking_factory import (
    CancelledBookingFactory,
    ConfirmedBookingFactory,
    ExpiredBookingFactory,
    PendingPaymentBookingFactory,
)
from tests.common.factories.invoice_factory import InvoiceFactory, InvoiceItemFactory


class TestCreatePaymentPayPalEndpoint(_TestBasePayPalEndpoints):
    def endpoint(self):
        return f'{self.base_path}/create-payment'

    @pytest.mark.parametrize(
        'booking',
        (
            lambda: PendingPaymentBookingFactory(),
            lambda: InvoiceFactory(booking=ConfirmedBookingFactory()).booking,
            lambda: InvoiceFactory(booking=CancelledBookingFactory()).booking,
            lambda: InvoiceFactory(booking=ExpiredBookingFactory()).booking,
        ),
        ids=[],
    )
    def test_booking_not_found(self, booking):
        response = self.client.post(url=self.endpoint(), json={'booking_id': str(booking().id)}, exp_code=404)

        assert response.json() == {'detail': 'Booking not found'}

    def test_no_approve_link(self, app):
        booking = PendingPaymentBookingFactory()
        invoice = InvoiceFactory(booking=booking)
        [InvoiceItemFactory(invoice=invoice) for _ in range(2)]
        order_id = uuid.uuid4().hex[:17]

        mock_paypal_provider = MagicMock(spec=PayPalProvider)
        mock_paypal_provider.create_order.return_value = {
            'id': order_id,
            'links': [
                {
                    'href': f'{self.paypal_api_base}/v2/checkout/orders/{order_id}',
                    'method': 'GET',
                    'rel': 'self',
                },
                {
                    'href': f'{self.paypal_api_base}/v2/checkout/orders/{order_id}',
                    'method': 'PATCH',
                    'rel': 'update',
                },
                {
                    'href': f'{self.paypal_api_base}/v2/checkout/orders/{order_id}/capture',
                    'method': 'POST',
                    'rel': 'capture',
                },
            ],
            'status': PayPalOrderStatus.CREATED.value,
        }

        mock_booking_service = BookingService(paypal_provider=mock_paypal_provider)
        mock_payment_service = MagicMock(spec=PaymentService)

        with (
            app.container.booking_service.override(mock_booking_service),
            app.container.payment_service.override(mock_payment_service),
        ):
            response = self.client.post(url=self.endpoint(), json={'booking_id': str(booking.id)}, exp_code=500)

        mock_payment_service.create.assert_called_once_with(
            **{
                'booking_id': booking.id,
                'provider': PaymentProvider.PAYPAL.value,
                'amount': invoice.total_price,
                'currency': invoice.currency,
            }
        )
        mock_paypal_provider.create_order.assert_called_once_with(
            payload={
                'intent': PayPalIntent.CAPTURE.value,
                'purchase_units': [{'amount': {'currency_code': invoice.currency, 'value': str(invoice.total_price)}}],
            }
        )
        assert response.json() == {'detail': 'No approve link returned by PayPal'}
        with self.app.container.session() as session:
            assert session.query(Payment).filter().count() == 0

    def test_create_payment_services_are_mocked(self, app):
        booking = PendingPaymentBookingFactory()
        invoice = InvoiceFactory(booking=booking)
        [InvoiceItemFactory(invoice=invoice) for _ in range(2)]
        order_id = uuid.uuid4().hex[:17]
        approve_link = f'https://www.sandbox.paypal.com/checkoutnow?token={order_id}'

        mock_paypal_provider = MagicMock(spec=PayPalProvider)
        mock_paypal_provider.create_order.return_value = {
            'id': order_id,
            'links': [
                {
                    'href': f'{self.paypal_api_base}/v2/checkout/orders/{order_id}',
                    'method': 'GET',
                    'rel': 'self',
                },
                {
                    'href': approve_link,
                    'method': 'GET',
                    'rel': 'approve',
                },
                {
                    'href': f'{self.paypal_api_base}/v2/checkout/orders/{order_id}',
                    'method': 'PATCH',
                    'rel': 'update',
                },
                {
                    'href': f'{self.paypal_api_base}/v2/checkout/orders/{order_id}/capture',
                    'method': 'POST',
                    'rel': 'capture',
                },
            ],
            'status': PayPalOrderStatus.CREATED.value,
        }

        mock_booking_service = BookingService(paypal_provider=mock_paypal_provider)
        mock_payment_service = MagicMock(spec=PaymentService)

        with (
            app.container.booking_service.override(mock_booking_service),
            app.container.payment_service.override(mock_payment_service),
        ):
            response = self.client.post(url=self.endpoint(), json={'booking_id': str(booking.id)})

        mock_payment_service.create.assert_called_once_with(
            **{
                'booking_id': booking.id,
                'provider': PaymentProvider.PAYPAL.value,
                'amount': invoice.total_price,
                'currency': invoice.currency,
            }
        )
        mock_paypal_provider.create_order.assert_called_once_with(
            payload={
                'intent': PayPalIntent.CAPTURE.value,
                'purchase_units': [{'amount': {'currency_code': invoice.currency, 'value': str(invoice.total_price)}}],
            }
        )
        mock_payment_service.update.assert_called_once_with(ANY, **{'provider_payment_id': order_id})
        assert response.json() == {'order_id': order_id, 'approve_link': approve_link}

    def test_create_payment(self, app):
        booking = PendingPaymentBookingFactory()
        invoice = InvoiceFactory(booking=booking)
        [InvoiceItemFactory(invoice=invoice) for _ in range(2)]
        order_id = uuid.uuid4().hex[:17]
        approve_link = f'https://www.sandbox.paypal.com/checkoutnow?token={order_id}'

        mock_paypal_provider = MagicMock(spec=PayPalProvider)
        mock_paypal_provider.create_order.return_value = {
            'id': order_id,
            'links': [
                {
                    'href': f'{self.paypal_api_base}/v2/checkout/orders/{order_id}',
                    'method': 'GET',
                    'rel': 'self',
                },
                {
                    'href': approve_link,
                    'method': 'GET',
                    'rel': 'approve',
                },
                {
                    'href': f'{self.paypal_api_base}/v2/checkout/orders/{order_id}',
                    'method': 'PATCH',
                    'rel': 'update',
                },
                {
                    'href': f'{self.paypal_api_base}/v2/checkout/orders/{order_id}/capture',
                    'method': 'POST',
                    'rel': 'capture',
                },
            ],
            'status': PayPalOrderStatus.CREATED.value,
        }

        mock_booking_service = BookingService(paypal_provider=mock_paypal_provider)

        with app.container.booking_service.override(mock_booking_service):
            response = self.client.post(url=self.endpoint(), json={'booking_id': str(booking.id)})

        mock_paypal_provider.create_order.assert_called_once_with(
            payload={
                'intent': PayPalIntent.CAPTURE.value,
                'purchase_units': [{'amount': {'currency_code': invoice.currency, 'value': str(invoice.total_price)}}],
            }
        )
        assert response.json() == {'order_id': order_id, 'approve_link': approve_link}

        with self.app.container.session() as session:
            query = session.query(Payment).filter()
            assert query.count() == 1

            found_payment = query.first()
            assert found_payment.booking_id == booking.id
            assert found_payment.provider == PaymentProvider.PAYPAL.value
            assert found_payment.amount == invoice.total_price
            assert found_payment.currency == invoice.currency
