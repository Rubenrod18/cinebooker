from decimal import Decimal, ROUND_HALF_UP

from app.models import Booking, Discount
from app.services import core
from app.utils import financials


class PriceCalculatorService(core.AbstractDomainService):
    @staticmethod
    def apply_discount(
        price: Decimal, discount: Discount | None = None, round_to: Decimal | None = Decimal('0.01')
    ) -> Decimal:
        if discount is None:
            return price

        if discount.is_percentage:
            discounted_price = price * (Decimal('1') - Decimal(discount.amount) / Decimal('100'))
        else:
            discounted_price = price - Decimal(discount.amount)

        if round_to is not None:
            discounted_price.quantize(round_to, rounding=ROUND_HALF_UP)
        return discounted_price

    @staticmethod
    def calculate_seat_invoice_item(booking: Booking, vat_rate: Decimal) -> dict:
        quantity = len(booking.booking_seats)
        unit_price = booking.booking_seats[0].base_price
        base_price = unit_price * Decimal(str(quantity))
        vat_price = financials.calculate_vat_amount(base_price, vat_rate)

        return {
            'quantity': quantity,
            'unit_price': unit_price,
            'base_price': base_price,
            'vat_rate': vat_rate,
            'vat_price': vat_price,
            'total_price': base_price + vat_price,
        }

    @staticmethod
    def calculate_invoice_prices(
        seat_invoice_item: dict, discount_invoice_item: dict, vat_rate: Decimal
    ) -> dict[str, Decimal]:
        return {
            'total_base_price': seat_invoice_item['base_price'] + discount_invoice_item['base_price'],
            'vat_rate': vat_rate,
            'total_vat_price': seat_invoice_item['vat_price'] + discount_invoice_item['vat_price'],
            'total_price': seat_invoice_item['total_price'] + discount_invoice_item['total_price'],
        }

    def calculate_discount_invoice_item(self, booking: Booking, vat_rate: Decimal) -> dict:
        calculated_data = {
            'quantity': 0,
            'unit_price': 0,
            'base_price': 0,
            'vat_rate': 0,
            'vat_price': 0,
            'total_price': 0,
        }

        if not booking.discount:
            return calculated_data

        total_base_price = sum(seat.base_price for seat in booking.booking_seats)
        discounted_price = self.apply_discount(total_base_price, booking.discount)
        discount_amount = total_base_price - discounted_price
        vat_amount = financials.calculate_vat_amount(discount_amount, vat_rate)

        return {
            'quantity': 1,
            'unit_price': 0,
            'base_price': -discount_amount,
            'vat_rate': vat_rate,
            'vat_price': -vat_amount,
            'total_price': -(discount_amount + vat_amount),
        }
