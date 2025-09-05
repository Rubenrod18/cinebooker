from datetime import timedelta

import factory

from app.models import Ticket
from app.models.booking import BookingStatus
from app.models.ticket import TicketBarcodeType, TicketStatus
from tests.common.factories.base_factory import BaseFactory
from tests.common.factories.booking_factory import BookingSeatFactory


class TicketFactory(BaseFactory):
    class Meta:
        model = Ticket

    booking_seat = factory.SubFactory(BookingSeatFactory)

    ticket_code = factory.Sequence(lambda n: f'Ticket_code_{n}')
    barcode_value = factory.Sequence(lambda n: f'Barcode_{n}')
    barcode_type = factory.Iterator(TicketBarcodeType.to_list())
    status = factory.Iterator(TicketStatus.to_list())
    issued_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')

    @factory.lazy_attribute
    def redeemed_at(self):
        booking = self.booking_seat.booking
        redeemed_at = None

        if booking.status == BookingStatus.CONFIRMED and self.status == TicketStatus.REDEEMED:
            redeemed_at = self.issued_at + timedelta(days=1)

        return redeemed_at
