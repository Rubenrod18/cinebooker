from datetime import datetime, timedelta, UTC

import pytest

from app.models import Ticket
from app.models.ticket import TicketStatus
from tests.acceptance.routers.ticket._base_ticket_test import _TestBaseTicketEndpoints
from tests.common.factories.booking_factory import (
    CancelledBookingFactory,
    ExpiredBookingFactory,
    PendingPaymentBookingFactory,
)
from tests.common.factories.ticket_factory import IssuedTicketFactory, RedeemedTicketFactory


class TestCreateTicketEndpoint(_TestBaseTicketEndpoints):
    def endpoint(self):
        return f'{self.base_path}/verify'

    def test_ticket_not_found(self):
        response = self.client.post(url=self.endpoint(), json={'barcode_value': 'fake'}, exp_code=404)

        assert response.json() == {'detail': 'Ticket not found'}

    def test_ticket_already_used(self):
        ticket = RedeemedTicketFactory()

        response = self.client.post(url=self.endpoint(), json={'barcode_value': ticket.barcode_value}, exp_code=422)

        assert response.json() == {'detail': 'Ticket already used'}

    @pytest.mark.parametrize(
        'booking_factory',
        [PendingPaymentBookingFactory, CancelledBookingFactory, ExpiredBookingFactory],
        ids=['pending_payment', 'cancelled', 'expired'],
    )
    def test_unpaid_booking(self, booking_factory):
        ticket = IssuedTicketFactory(
            booking_seat__booking__showtime__start_time=datetime.now(UTC) - timedelta(days=1),
            booking_seat__booking=booking_factory(),
        )

        response = self.client.post(url=self.endpoint(), json={'barcode_value': ticket.barcode_value}, exp_code=422)

        assert response.json() == {'detail': 'Unpaid Booking'}

    def test_showtime_already_started_or_expired(self):
        ticket = IssuedTicketFactory(booking_seat__booking__showtime__start_time=datetime.now(UTC) - timedelta(days=1))

        response = self.client.post(url=self.endpoint(), json={'barcode_value': ticket.barcode_value}, exp_code=422)

        assert response.json() == {'detail': 'Showtime already started or expired'}

    def test_verify_ticket(self):
        ticket = IssuedTicketFactory()

        response = self.client.post(url=self.endpoint(), json={'barcode_value': ticket.barcode_value}, exp_code=204)

        assert not response.text

        with self.app.container.session() as session:
            found_ticket = session.query(Ticket).filter(Ticket.barcode_value == ticket.barcode_value).first()
            assert found_ticket
            assert found_ticket.status == TicketStatus.REDEEMED
            assert isinstance(found_ticket.redeemed_at, datetime)
