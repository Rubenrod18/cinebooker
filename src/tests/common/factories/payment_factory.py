import random
from datetime import datetime, UTC
from decimal import Decimal

import factory

from app.models import Payment
from app.models.payment import PaymentProvider, PaymentStatus
from tests.common.factories.base_factory import BaseFactory
from tests.common.factories.booking_factory import BookingFactory, PendingPaymentBookingFactory
from tests.conftest import fake


def paypal_metadata(amount: Decimal, currency: str):
    currency = currency or 'EUR'
    amount = amount or Decimal('10.00')
    return {
        'order_id': f'PAY-{fake.uuid4()}',
        'capture_id': f'CPT-{fake.uuid4()}',
        'payer_id': fake.uuid4(),
        'intent': random.choice(['CAPTURE', 'AUTHORIZE']),
        'status': random.choice(['COMPLETED', 'PENDING', 'DENIED']),
        'amount': str(amount),
        'currency': currency,
        'created_at': datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
    }


def stripe_metadata():
    return {'payment_id': fake.random_int()}


class PaymentFactory(BaseFactory):
    class Meta:
        model = Payment

    booking = factory.SubFactory(BookingFactory)

    provider = factory.Iterator(PaymentProvider.to_list())
    provider_payment_id = factory.Maybe(
        'has_provider_payment_id',
        yes_declaration=factory.Sequence(lambda n: f'Payment_provider_payment_id_{n}'),
        no_declaration=None,
    )
    amount = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
    currency = factory.Iterator(['eur', 'usd', 'gbp'])  # NOTE: PayPal supports fewer currencies than Stripe.
    status = factory.Iterator(PaymentStatus.to_list())
    created_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    updated_at = factory.Faker('date_time_between', start_date='-1y', end_date='now')

    @factory.lazy_attribute
    def provider_metadata(self):
        value = stripe_metadata()
        prov = self.provider.lower()

        if 'paypal' in prov:
            value = paypal_metadata(self.amount, self.currency)

        return value


class PendingStripePaymentFactory(PaymentFactory):
    booking = factory.SubFactory(PendingPaymentBookingFactory)
    status = PaymentStatus.PENDING.value
    provider = PaymentProvider.STRIPE.value


class PendingPayPalPalPaymentFactory(PaymentFactory):
    booking = factory.SubFactory(PendingPaymentBookingFactory)
    status = PaymentStatus.PENDING.value
    provider = PaymentProvider.PAYPAL.value
