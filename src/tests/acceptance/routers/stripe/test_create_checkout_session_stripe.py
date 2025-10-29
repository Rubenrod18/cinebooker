from unittest.mock import ANY, MagicMock

from app.models.payment import PaymentProvider
from app.providers.stripe_provider import StripeProvider
from app.services.booking_service import BookingService
from app.services.payment_service import PaymentService
from app.utils.financials import decimal_to_int
from tests.acceptance.routers.stripe._base_stripe_test import _TestBaseStripeEndpoints
from tests.common.factories.booking_factory import PendingPaymentBookingFactory
from tests.common.factories.invoice_factory import InvoiceFactory, InvoiceItemFactory
from tests.conftest import fake


class TestCreateCheckoutSessionStripeEndpoint(_TestBaseStripeEndpoints):
    def test_create_checkout_session(self, app):
        checkout_session_url = fake.url()
        stripe_checkout_session_id = fake.random_int()
        booking = PendingPaymentBookingFactory()
        invoice = InvoiceFactory(booking=booking)
        invoice_items = [InvoiceItemFactory(invoice=invoice) for _ in range(2)]

        mock_stripe_provider = MagicMock(spec=StripeProvider)
        stripe_checkout_session = MagicMock()
        stripe_checkout_session.id = stripe_checkout_session_id
        stripe_checkout_session.url = checkout_session_url
        mock_stripe_provider.create_checkout_session.return_value = stripe_checkout_session

        mock_booking_service = BookingService(stripe_provider=mock_stripe_provider)
        mock_payment_service = MagicMock(spec=PaymentService)

        with (
            app.container.booking_service.override(mock_booking_service),
            app.container.payment_service.override(mock_payment_service),
        ):
            response = self.client.post(url=f'{self.base_path}/session', json={'booking_id': str(booking.id)})

        mock_payment_service.create.assert_called_once_with(
            **{
                'booking_id': booking.id,
                'provider': PaymentProvider.STRIPE.value,
                'amount': booking.invoice.total_price,
                'currency': booking.invoice.currency,
            }
        )
        expected_invoice_items = [
            {
                'price_data': {
                    'currency': invoice.currency,
                    'product_data': {
                        'name': invoice_item.description,
                    },
                    'unit_amount': decimal_to_int(invoice_item.total_price),
                },
                'quantity': decimal_to_int(invoice_item.quantity),
            }
            for invoice_item in invoice_items
        ]
        mock_stripe_provider.create_checkout_session.assert_called_once_with(
            mode='payment',
            payment_method_types=['card'],
            line_items=expected_invoice_items,
            success_url='https://stripe.com/success',
            metadata={'payment_id': ANY},
            payment_intent_data={'metadata': {'payment_id': ANY}},
        )
        assert response.json() == {'url': checkout_session_url}
