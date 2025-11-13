from decimal import Decimal
from unittest.mock import ANY

from iso4217 import Currency

from app.models import Invoice, InvoiceItem
from app.models.invoice import InvoiceStatus
from app.utils import financials
from tests.acceptance.routers.booking._base_booking_test import _TestBaseBookingEndpoints
from tests.common.factories.booking_factory import PendingPaymentBookingSeatFactory
from tests.common.factories.discount_factory import EnabledDiscountFactory


class TestCreateBookingEndpoint(_TestBaseBookingEndpoints):
    # TODO: Pending to add more test cases
    def endpoint(self, booking_id: str) -> str:
        return f'{self.base_path}/{booking_id}/invoices'

    def test_create_invoice_without_discounts(self):
        base_price = Decimal('5.00')
        vat_rate = Decimal('0.21')
        price_with_vat = financials.apply_vat_rate(base_price, vat_rate)
        booking_seat = PendingPaymentBookingSeatFactory(
            base_price=base_price,
            vat_rate=vat_rate,
            price_with_vat=price_with_vat,
        )
        booking = booking_seat.booking
        total_vat_price = financials.calculate_vat_amount(base_price, vat_rate)

        response = self.client.post(url=self.endpoint(str(booking.id)), json={})
        json_response = response.json()

        assert json_response == {
            'booking_id': str(booking.id),
            'code': ANY,
            'currency': Currency.EUR.value,
            'total_base_price': str(base_price),
            'vat_rate': str(vat_rate),
            'total_vat_price': str(total_vat_price),
            'total_price': str(price_with_vat),
            'status': InvoiceStatus.ISSUED.value,
            'created_at': ANY,
            'updated_at': ANY,
        }

        with self.app.container.session() as session:
            invoice = session.query(Invoice).first()
            assert invoice
            assert invoice.booking == booking
            assert isinstance(int(invoice.code), int)
            assert invoice.currency == Currency.EUR.value
            assert invoice.total_base_price == base_price
            assert invoice.vat_rate == vat_rate
            assert invoice.total_vat_price == total_vat_price
            assert invoice.total_price == price_with_vat
            assert invoice.status == InvoiceStatus.ISSUED.value

            invoice_item = session.query(InvoiceItem).first()
            vat_price = financials.calculate_vat_amount(booking_seat.base_price, invoice.vat_rate)
            assert invoice_item
            assert invoice_item.invoice_id == invoice.id
            assert invoice_item.description == 'Seats'
            assert invoice_item.quantity == 1
            assert invoice_item.unit_price == booking_seat.base_price
            assert invoice_item.base_price == booking_seat.base_price
            assert invoice_item.vat_rate == invoice.vat_rate
            assert invoice_item.vat_price == vat_price
            assert invoice_item.total_price == booking_seat.base_price + vat_price

    def test_create_invoice_with_discounts(self):
        base_price = Decimal('5.00')
        vat_rate = Decimal('0.21')
        price_with_vat = financials.apply_vat_rate(base_price, vat_rate)
        discount = EnabledDiscountFactory(
            is_percentage=False,
            amount=Decimal('1.50'),
            usages_limit=None,
        )
        booking_seat = PendingPaymentBookingSeatFactory(
            booking__discount=discount,
            base_price=base_price,
            vat_rate=vat_rate,
            price_with_vat=price_with_vat,
        )
        booking = booking_seat.booking
        PendingPaymentBookingSeatFactory(
            booking=booking,
            booking__discount=discount,
            base_price=base_price,
            vat_rate=vat_rate,
            price_with_vat=price_with_vat,
        )

        response = self.client.post(url=self.endpoint(str(booking.id)), json={})
        json_response = response.json()

        assert json_response == {
            'booking_id': str(booking.id),
            'code': ANY,
            'currency': Currency.EUR.value,
            'total_base_price': '8.50',
            'vat_rate': str(vat_rate),
            'total_vat_price': '1.78',
            'total_price': '10.28',
            'status': InvoiceStatus.ISSUED.value,
            'created_at': ANY,
            'updated_at': ANY,
        }

        with self.app.container.session() as session:
            invoice = session.query(Invoice).first()

            seat_invoice_item = session.query(InvoiceItem).first()

            assert seat_invoice_item
            assert seat_invoice_item.invoice_id == invoice.id
            assert seat_invoice_item.description == 'Seats'
            assert seat_invoice_item.quantity == 2
            assert seat_invoice_item.unit_price == Decimal('5.00')
            assert seat_invoice_item.base_price == Decimal('10.00')
            assert seat_invoice_item.vat_rate == vat_rate
            assert seat_invoice_item.vat_price == Decimal('2.10')
            assert seat_invoice_item.total_price == Decimal('12.10')

            discount_invoice_item = session.query(InvoiceItem).order_by(InvoiceItem.created_at.desc()).first()
            assert discount_invoice_item
            assert discount_invoice_item.invoice_id == invoice.id
            assert discount_invoice_item.description == f'Discount {booking.discount.code}'
            assert discount_invoice_item.quantity == 1
            assert discount_invoice_item.unit_price == Decimal('0')
            assert discount_invoice_item.base_price == Decimal('-1.50')
            assert discount_invoice_item.vat_rate == vat_rate
            assert discount_invoice_item.vat_price == Decimal('-0.32')
            assert discount_invoice_item.total_price == Decimal('-1.82')

            assert invoice
            assert invoice.booking == booking
            assert isinstance(int(invoice.code), int)
            assert invoice.currency == Currency.EUR.value
            assert invoice.total_base_price == Decimal('8.50')
            assert invoice.vat_rate == vat_rate
            assert invoice.total_vat_price == Decimal('1.78')
            assert invoice.total_price == Decimal('10.28')
            assert invoice.status == InvoiceStatus.ISSUED.value
