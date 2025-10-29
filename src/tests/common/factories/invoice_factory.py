from decimal import Decimal

import factory

from app.models import Invoice
from app.models.invoice import InvoiceItem, InvoiceStatus
from tests.common.factories.base_factory import BaseFactory
from tests.common.factories.booking_factory import BookingFactory
from tests.conftest import fake


class InvoiceFactory(BaseFactory):
    class Meta:
        model = Invoice

    booking = factory.SubFactory(BookingFactory)

    code = factory.Sequence(lambda n: f'Invoice_code_{n}')
    currency = factory.LazyFunction(lambda: fake.currency_code().lower())
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
