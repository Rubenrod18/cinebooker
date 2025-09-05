from app.models import Booking
from app.models.booking import BookingStatus

from ..factories.invoice_factory import InvoiceFactory
from . import seed_actions
from .core import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='InvoiceSeeder', priority=8, factory=InvoiceFactory)
        self._session = self.factory.get_db_session()

    def _create_invoices(self):
        bookings = self._session.query(Booking).filter(Booking.status == BookingStatus.CONFIRMED).all()

        for booking in bookings:
            self.factory.create(booking=booking)

    @seed_actions
    def seed(self, rows: int = None) -> None:
        self._create_invoices()
