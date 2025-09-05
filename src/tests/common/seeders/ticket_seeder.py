from app.models import Booking
from app.models.booking import BookingSeat, BookingStatus

from ..factories.ticket_factory import TicketFactory
from . import seed_actions
from .core import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='TicketSeeder', priority=7, factory=TicketFactory)
        self._session = self.factory.get_db_session()

    def _create_tickets(self):
        booking_seats = (
            self._session.query(BookingSeat)
            .outerjoin(Booking, BookingSeat.booking_id == Booking.id)
            .filter(Booking.status == BookingStatus.CONFIRMED)
            .all()
        )

        for booking_seat in booking_seats:
            self.factory.create(booking_seat=booking_seat)

    @seed_actions
    def seed(self, rows: int = None) -> None:
        self._create_tickets()
