import base64
import os
from unittest.mock import MagicMock

from app.models import Booking, Invoice, Payment
from app.models.booking import BookingStatus
from app.models.invoice import InvoiceStatus
from app.models.payment import PaymentStatus
from app.providers import paypal_provider
from app.providers.paypal_provider import PayPalWebhookVerificationStatus
from app.services.booking_service import BookingService
from tests.acceptance.routers.paypal._base_paypal_test import _TestBasePayPalEndpoints
from tests.common.factories.booking_factory import PendingPaymentBookingFactory
from tests.common.factories.invoice_factory import InvoiceItemFactory, IssuedInvoiceFactory
from tests.common.factories.payment_factory import (
    PendingPayPalPalPaymentFactory,
)
from tests.conftest import fake


class TestWebhookPayPalEndpoint(_TestBasePayPalEndpoints):
    def endpoint(self):
        return f'{self.base_path}/webhook'

    def test_missing_paypal_headers(self):
        response = self.client.post(url=self.endpoint(), json={}, exp_code=400)

        assert response.json() == {'detail': 'Missing PayPal headers'}

    def test_verification_status_is_not_equal_to_success(self, app):
        random_bytes = os.urandom(48)  # NOTE: 48 bytes ≈ 64 chars when base64 encoded
        fake_signature = base64.b64encode(random_bytes).decode('utf-8')

        mock_paypal_provider = MagicMock(spec=paypal_provider.PayPalProvider)
        mock_paypal_provider.verify_webhook_signature.return_value = {
            'verification_status': PayPalWebhookVerificationStatus.FAILURE.value
        }
        mock_booking_service = BookingService(paypal_provider=mock_paypal_provider)

        with app.container.booking_service.override(mock_booking_service):
            response = self.client.post(
                url=self.endpoint(),
                json={},
                headers={
                    'PAYPAL-TRANSMISSION-ID': fake.uuid4(),
                    'PAYPAL-TRANSMISSION-TIME': fake.iso8601(tzinfo=None),  # e.g. "2025-10-30T14:25:43Z"
                    'PAYPAL-CERT-URL': f'{self.paypal_api_base}/certs/CERT-{fake.hexify(text="^^^^^^^^^^^^^^^^")}',
                    'PAYPAL-AUTH-ALGO': 'SHA256withRSA',
                    'PAYPAL-TRANSMISSION-SIG': fake_signature,
                },
                exp_code=400,
            )

        assert response.json() == {'detail': 'Invalid webhook signature'}

    def test_payment_record_not_found(self, app):
        random_bytes = os.urandom(48)  # NOTE: 48 bytes ≈ 64 chars when base64 encoded
        fake_signature = base64.b64encode(random_bytes).decode('utf-8')

        mock_paypal_provider = MagicMock(spec=paypal_provider.PayPalProvider)
        mock_paypal_provider.verify_webhook_signature.return_value = {
            'verification_status': PayPalWebhookVerificationStatus.SUCCESS.value
        }
        mock_booking_service = BookingService(paypal_provider=mock_paypal_provider)

        with app.container.booking_service.override(mock_booking_service):
            response = self.client.post(
                url=self.endpoint(),
                json={
                    'event_type': paypal_provider.PayPalEventType.PAYMENT_CAPTURE_COMPLETED.value,
                    'resource': {'id': None},
                },
                headers={
                    'PAYPAL-TRANSMISSION-ID': fake.uuid4(),
                    'PAYPAL-TRANSMISSION-TIME': fake.iso8601(tzinfo=None),  # e.g. "2025-10-30T14:25:43Z"
                    'PAYPAL-CERT-URL': f'{self.paypal_api_base}/certs/CERT-{fake.hexify(text="^^^^^^^^^^^^^^^^")}',
                    'PAYPAL-AUTH-ALGO': 'SHA256withRSA',
                    'PAYPAL-TRANSMISSION-SIG': fake_signature,
                },
                exp_code=404,
            )

        assert response.json() == {'detail': 'Payment not found'}

    def test_webhook_payment_success(self, app):
        booking = PendingPaymentBookingFactory()
        payment = PendingPayPalPalPaymentFactory(booking=booking)
        invoice = IssuedInvoiceFactory(booking=booking)
        [InvoiceItemFactory(invoice=invoice) for _ in range(2)]

        random_bytes = os.urandom(48)  # NOTE: 48 bytes ≈ 64 chars when base64 encoded
        fake_signature = base64.b64encode(random_bytes).decode('utf-8')

        mock_paypal_provider = MagicMock(spec=paypal_provider.PayPalProvider)
        mock_paypal_provider.verify_webhook_signature.return_value = {
            'verification_status': PayPalWebhookVerificationStatus.SUCCESS.value
        }

        mock_booking_service = BookingService(paypal_provider=mock_paypal_provider)

        with app.container.booking_service.override(mock_booking_service):
            self.client.post(
                url=self.endpoint(),
                json={
                    'event_type': paypal_provider.PayPalEventType.PAYMENT_CAPTURE_COMPLETED.value,
                    'resource': {'id': payment.provider_payment_id},
                },
                headers={
                    'PAYPAL-TRANSMISSION-ID': fake.uuid4(),
                    'PAYPAL-TRANSMISSION-TIME': fake.iso8601(tzinfo=None),  # e.g. "2025-10-30T14:25:43Z"
                    'PAYPAL-CERT-URL': f'{self.paypal_api_base}/certs/CERT-{fake.hexify(text="^^^^^^^^^^^^^^^^")}',
                    'PAYPAL-AUTH-ALGO': 'SHA256withRSA',
                    'PAYPAL-TRANSMISSION-SIG': fake_signature,
                },
                exp_code=204,
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

    def test_webhook_payment_cancelled(self, app):
        booking = PendingPaymentBookingFactory()
        payment = PendingPayPalPalPaymentFactory(booking=booking)
        invoice = IssuedInvoiceFactory(booking=booking)
        [InvoiceItemFactory(invoice=invoice) for _ in range(2)]
        resource = {'id': payment.provider_payment_id}

        random_bytes = os.urandom(48)  # NOTE: 48 bytes ≈ 64 chars when base64 encoded
        fake_signature = base64.b64encode(random_bytes).decode('utf-8')

        mock_paypal_provider = MagicMock(spec=paypal_provider.PayPalProvider)
        mock_paypal_provider.verify_webhook_signature.return_value = {
            'verification_status': PayPalWebhookVerificationStatus.SUCCESS.value
        }

        mock_booking_service = BookingService(paypal_provider=mock_paypal_provider)

        with app.container.booking_service.override(mock_booking_service):
            self.client.post(
                url=self.endpoint(),
                json={
                    'event_type': paypal_provider.PayPalEventType.PAYMENT_CAPTURE_DENIED.value,
                    'resource': resource,
                },
                headers={
                    'PAYPAL-TRANSMISSION-ID': fake.uuid4(),
                    'PAYPAL-TRANSMISSION-TIME': fake.iso8601(tzinfo=None),  # e.g. "2025-10-30T14:25:43Z"
                    'PAYPAL-CERT-URL': f'{self.paypal_api_base}/certs/CERT-{fake.hexify(text="^^^^^^^^^^^^^^^^")}',
                    'PAYPAL-AUTH-ALGO': 'SHA256withRSA',
                    'PAYPAL-TRANSMISSION-SIG': fake_signature,
                },
                exp_code=204,
            )

        with self.app.container.session() as session:
            query = session.query(Payment).filter()
            assert query.count() == 1

            found_payment = query.first()
            assert found_payment.booking_id == booking.id
            assert found_payment.status == PaymentStatus.CANCELLED
            assert found_payment.provider_payment_id == payment.provider_payment_id
            assert found_payment.provider_metadata == resource

            query = session.query(Booking).filter()
            assert query.count() == 1

            found_booking = query.first()
            assert found_booking.id == found_payment.booking_id
            assert found_booking.status == BookingStatus.CANCELLED

            query = session.query(Invoice).filter()
            assert query.count() == 1

            found_invoice = query.first()
            assert found_invoice.id == invoice.id
            assert found_invoice.status == InvoiceStatus.ISSUED
