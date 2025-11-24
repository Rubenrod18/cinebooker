import json
import os
from dataclasses import asdict, dataclass
from unittest.mock import MagicMock

from app.models import Booking, Invoice, Payment
from app.models.booking import BookingStatus
from app.models.invoice import InvoiceStatus
from app.models.payment import PaymentStatus
from app.providers.stripe_provider import StripeEventType, StripeProvider
from app.services.invoice_service import InvoiceService
from app.services.payment_service import PaymentService
from tests.acceptance.routers.stripe._base_stripe_test import _TestBaseStripeEndpoints
from tests.common.factories.booking_factory import PendingPaymentBookingFactory
from tests.common.factories.invoice_factory import IssuedInvoiceFactory
from tests.common.factories.payment_factory import PendingStripePaymentFactory
from tests.conftest import fake


@dataclass
class WebhookEvent:
    type: str
    data: dict

    def to_dict(self) -> dict:
        return asdict(self)


class TestWebhookStripeEndpoint(_TestBaseStripeEndpoints):
    def test_webhook_payment_success(self, app):
        header_stripe_signature = fake.pystr(min_chars=32, max_chars=32)
        payload = {'data': ''}

        booking = PendingPaymentBookingFactory()
        payment = PendingStripePaymentFactory(booking=booking)
        invoice = IssuedInvoiceFactory(booking=booking)

        mock_stripe_provider = MagicMock(spec=StripeProvider)
        mock_stripe_provider.verify_webhook.return_value = WebhookEvent(
            type=StripeEventType.PAYMENT_INTENT_SUCCEEDED.value,
            data={'object': {'id': payment.provider_payment_id, 'metadata': {'payment_id': payment.id}}},
        )

        mock_payment_service = MagicMock(spec=PaymentService)
        mock_payment_service.find_by_id.return_value = payment

        mock_invoice_service = MagicMock(spec=InvoiceService)
        mock_invoice_service.paid.return_value = invoice

        with app.container.stripe_provider.override(mock_stripe_provider):
            self.client.post(
                url=f'{self.base_path}/webhook',
                json=payload,
                headers={'Stripe-Signature': header_stripe_signature},
                exp_code=204,
            )

        mock_stripe_provider.verify_webhook.assert_called_once_with(
            json.dumps(payload, separators=(',', ':')).encode('utf-8'),
            sig_header=header_stripe_signature,
            webhook_secret=os.getenv('STRIPE_WEBHOOK_SECRET'),
        )

        with self.app.container.session() as session:
            query = session.query(Payment).filter()
            assert query.count() == 1

            found_payment = query.first()
            assert found_payment.booking_id == booking.id
            assert found_payment.status == PaymentStatus.COMPLETED
            assert found_payment.provider_payment_id == payment.provider_payment_id
            assert found_payment.provider_metadata is None

            query = session.query(Booking).filter()
            assert query.count() == 1

            found_booking = query.first()
            assert found_booking.id == found_payment.booking_id
            assert found_booking.status == BookingStatus.CONFIRMED

            query = session.query(Invoice).filter()
            assert query.count() == 1

            found_invoice = query.first()
            assert found_invoice.id == invoice.id
            assert found_invoice.status == InvoiceStatus.PAID

    def test_webhook_payment_failed(self, app):
        header_stripe_signature = fake.pystr(min_chars=32, max_chars=32)
        payment_error_message = 'Payment failed'
        payload = {'data': ''}

        booking = PendingPaymentBookingFactory()
        payment = PendingStripePaymentFactory(booking=booking)
        mock_stripe_provider = MagicMock(spec=StripeProvider)
        mock_stripe_provider.verify_webhook.return_value = WebhookEvent(
            type=StripeEventType.PAYMENT_INTENT_FAILED.value,
            data={
                'object': {
                    'id': payment.provider_payment_id,
                    'metadata': {'payment_id': payment.id},
                    'last_payment_error': {
                        'message': payment_error_message,
                    },
                }
            },
        )

        with app.container.stripe_provider.override(mock_stripe_provider):
            self.client.post(
                url=f'{self.base_path}/webhook',
                json=payload,
                headers={'Stripe-Signature': header_stripe_signature},
                exp_code=204,
            )

        mock_stripe_provider.verify_webhook.assert_called_once_with(
            json.dumps(payload, separators=(',', ':')).encode('utf-8'),
            sig_header=header_stripe_signature,
            webhook_secret=os.getenv('STRIPE_WEBHOOK_SECRET'),
        )

        with self.app.container.session() as session:
            query = session.query(Payment).filter()
            assert query.count() == 1

            found_payment = query.first()
            assert found_payment.booking_id == booking.id
            assert found_payment.status == PaymentStatus.FAILED
            assert found_payment.provider_payment_id == payment.provider_payment_id
            assert found_payment.provider_metadata == {'error_message': payment_error_message}
