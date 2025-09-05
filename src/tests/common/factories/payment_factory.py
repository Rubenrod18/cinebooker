import random
from datetime import datetime, UTC
from decimal import Decimal

import factory

from app.models import Payment
from app.models.payment import PaymentProvider, PaymentStatus
from tests.common.factories.base_factory import BaseFactory
from tests.common.factories.booking_factory import BookingFactory
from tests.conftest import faker


def paypal_metadata(amount: Decimal, currency: str):
    currency = currency or 'EUR'
    amount = amount or Decimal('10.00')
    return {
        'order_id': f'PAY-{faker.uuid4()}',
        'capture_id': f'CPT-{faker.uuid4()}',
        'payer_id': faker.uuid4(),
        'intent': random.choice(['CAPTURE', 'AUTHORIZE']),
        'status': random.choice(['COMPLETED', 'PENDING', 'DENIED']),
        'amount': str(amount),
        'currency': currency,
        'created_at': datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
    }


def stripe_metadata(amount: Decimal, currency: str):
    currency = currency or 'EUR'
    amount = amount or Decimal('10.00')
    return {
        'id': f'ch_{faker.pystr(min_chars=8, max_chars=12)}',
        'payment_method': random.choice(['credit', 'debit']),
        'status': random.choice(['succeeded', 'pending', 'requires_action']),
        'amount': int(amount * 100),  # Stripe often stores cents (int)
        'currency': currency.lower(),
        'charges': [{'id': f'ch_{faker.pystr(8)}', 'amount': int(amount * 100)}],
        'created': datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
    }


class PaymentFactory(BaseFactory):
    class Meta:
        model = Payment

    booking = factory.SubFactory(BookingFactory)

    provider = factory.Iterator(PaymentProvider.to_list())
    provider_payment_id = factory.Sequence(lambda n: f'Payment_provider_payment_id_{n}')
    amount = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
    currency = factory.Sequence(lambda n: f'Payment_Currency_{n}')
    status = factory.Iterator(PaymentStatus.to_list())

    @factory.lazy_attribute
    def provider_metadata(self):
        value = stripe_metadata(self.amount, self.currency)
        prov = self.provider.lower()

        if 'paypal' in prov:
            value = paypal_metadata(self.amount, self.currency)

        return value
