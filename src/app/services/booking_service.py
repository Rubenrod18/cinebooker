import stripe
from sqlmodel import Session

from app.models import Booking, Payment
from app.models.booking import BookingStatus
from app.providers.stripe_provider import StripeProvider
from app.repositories.booking_repository import BookingRepository
from app.services import core
from app.utils.financials import decimal_to_int


class BookingService(
    core.AbstractCreateService,
    core.FindByIdMixin,
    core.GetMixin,
    core.AbstractUpdateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        booking_repository: BookingRepository | None = None,
        stripe_provider: StripeProvider | None = None,
    ):
        super().__init__(repository=booking_repository or BookingRepository(session))
        self.stripe_provider = stripe_provider or StripeProvider()

    def create(self, **kwargs) -> Booking:
        kwargs['status'] = BookingStatus.PENDING_PAYMENT
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> Booking:
        return self.repository.update(record, **kwargs)

    def confirmed(self, record, **kwargs) -> Booking:
        kwargs['status'] = BookingStatus.CONFIRMED
        return self.update(record, **kwargs)

    def create_stripe_checkout_session(self, booking: Booking, payment: Payment) -> stripe.checkout.Session:
        invoice = booking.invoice
        line_items = [
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
            for invoice_item in invoice.invoice_items
        ]
        return self.stripe_provider.create_checkout_session(
            mode='payment',
            payment_method_types=['card'],
            line_items=line_items,
            # NOTE: Using Stripe’s URL as a placeholder; can be replaced once frontend routes are added.
            success_url='https://stripe.com/success',
            metadata={'payment_id': payment.id},
            payment_intent_data={'metadata': {'payment_id': payment.id}},
        )
