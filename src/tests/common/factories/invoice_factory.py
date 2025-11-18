from decimal import Decimal

import factory
from iso4217 import Currency

from app.models import Invoice
from app.models.invoice import InvoiceItem, InvoiceStatus
from tests.common.factories.base_factory import BaseFactory
from tests.common.factories.booking_factory import BookingFactory


class InvoiceFactory(BaseFactory):
    class Meta:
        model = Invoice

    booking = factory.SubFactory(BookingFactory)

    code = factory.Sequence(lambda n: f'Invoice_code_{n}')
    currency = factory.Iterator(
        [Currency.EUR.value, Currency.USD.value, Currency.GBP.value]
    )  # NOTE: PayPal supports fewer currencies than Stripe.
    total_base_price = factory.Faker(
        'pydecimal', left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20
    )
    vat_rate = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)
    status = factory.Iterator(InvoiceStatus.to_list())

    @factory.lazy_attribute
    def total_vat_price(self):
        return (self.total_base_price * self.vat_rate).quantize(Decimal('0.01'))

    @factory.lazy_attribute
    def total_price(self):
        return (self.total_base_price + self.total_vat_price).quantize(Decimal('0.01'))


class IssuedInvoiceFactory(InvoiceFactory):
    status = InvoiceStatus.ISSUED


class PaidInvoiceFactory(InvoiceFactory):
    status = InvoiceStatus.PAID


class InvoiceItemFactory(BaseFactory):
    class Meta:
        model = InvoiceItem

    invoice = factory.SubFactory(InvoiceFactory)

    description = factory.Faker('text')
    quantity = factory.Faker('pyint', min_value=1, max_value=10)
    unit_price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=5, max_value=20)
    vat_rate = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, min_value=0.05, max_value=0.25)

    @factory.lazy_attribute
    def base_price(self):
        return (self.quantity * self.unit_price).quantize(Decimal('0.01'))

    @factory.lazy_attribute
    def vat_price(self):
        return (self.base_price * self.vat_rate).quantize(Decimal('0.01'))

    @factory.lazy_attribute
    def total_price(self):
        return (self.base_price + self.vat_price).quantize(Decimal('0.01'))
