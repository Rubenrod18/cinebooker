import json
import os
from dataclasses import asdict, dataclass
from unittest.mock import MagicMock

from app.providers.stripe_provider import StripeEventType, StripeProvider
from app.services.booking_service import BookingService
from app.services.payment_service import PaymentService
from tests.acceptance.routers.stripe._base_stripe_test import _TestBaseStripeEndpoints
from tests.common.factories.booking_factory import PendingPaymentBookingFactory
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
        payment_intent_id = fake.pystr(min_chars=27, max_chars=27)
        payment_id = fake.random_int()
        header_stripe_signature = fake.pystr(min_chars=32, max_chars=32)
        payload = {'data': ''}

        booking = PendingPaymentBookingFactory()
        payment = PendingStripePaymentFactory(booking=booking)
        mock_stripe_provider = MagicMock(spec=StripeProvider)
        mock_stripe_provider.verify_webhook.return_value = WebhookEvent(
            type=StripeEventType.PAYMENT_INTENT_SUCCEEDED.value,
            data={'object': {'id': payment_intent_id, 'metadata': {'payment_id': payment_id}}},
        )
        mock_booking_service = MagicMock(spec=BookingService)

        mock_payment_service = MagicMock(spec=PaymentService)
        mock_payment_service.find_by_id.return_value = payment

        with (
            app.container.stripe_provider.override(mock_stripe_provider),
            app.container.booking_service.override(mock_booking_service),
            app.container.payment_service.override(mock_payment_service),
        ):
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
        mock_payment_service.find_by_id.assert_called_once_with(payment_id)
        mock_payment_service.completed.assert_called_once_with(
            payment, **{'provider_payment_id': payment_intent_id, 'provider_metadata': None}
        )
        mock_booking_service.confirmed.assert_called_once_with(booking)

    def test_webhook_payment_failed(self, app):
        payment_intent_id = fake.pystr(min_chars=27, max_chars=27)
        payment_id = fake.random_int()
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
                    'id': payment_intent_id,
                    'metadata': {'payment_id': payment_id},
                    'last_payment_error': {
                        'message': payment_error_message,
                    },
                }
            },
        )

        mock_payment_service = MagicMock(spec=PaymentService)
        mock_payment_service.find_by_id.return_value = payment

        with (
            app.container.stripe_provider.override(mock_stripe_provider),
            app.container.payment_service.override(mock_payment_service),
        ):
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
        mock_payment_service.find_by_id.assert_called_once_with(payment_id)
        mock_payment_service.failed.assert_called_once_with(
            payment,
            **{'provider_payment_id': payment_intent_id, 'provider_metadata': {'error_message': payment_error_message}},
        )
