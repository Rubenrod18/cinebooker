import uuid

from app.models import Booking
from app.models.booking import BookingStatus
from app.models.payment import PaymentStatus

from ..factories.payment_factory import PaymentFactory
from . import seed_actions
from .core import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='PaymentSeeder', priority=6, factory=PaymentFactory)
        self._session = self.factory.get_db_session()

    def _create_pending_payments(self):
        # CASE 1: The customer is starting the booking
        bookings = self._session.query(Booking).filter(Booking.status == BookingStatus.PENDING_PAYMENT).all()

        for booking in bookings:
            self.factory.create(booking=booking, status=PaymentStatus.PENDING)

    def _create_completed_payments(self):
        # CASE 2: The customer pays the booking
        bookings = self._session.query(Booking).filter(Booking.status == BookingStatus.CONFIRMED).all()

        for booking in bookings:
            self.factory.create(booking=booking, status=PaymentStatus.COMPLETED, provider_payment_id=uuid.uuid4().hex)

    def _create_cancelled_payments(self):
        # CASE 3: The customer decline the booking
        # CASE 4: There was a problem with the external payment provider
        bookings = self._session.query(Booking).filter(Booking.status == BookingStatus.CANCELLED).all()

        for i, booking in enumerate(bookings):
            status = PaymentStatus.CANCELLED if i % 2 == 0 else PaymentStatus.FAILED
            provider_metadata = {'message': 'Credit card invalid'} if status == PaymentStatus.FAILED else None
            self.factory.create(
                booking=booking,
                status=status,
                provider_payment_id=uuid.uuid4().hex,
                provider_metadata=provider_metadata,
            )

    def _create_expired_payments(self):
        # CASE 5: The customer's booking has been expired
        bookings = self._session.query(Booking).filter(Booking.status == BookingStatus.EXPIRED).all()

        for booking in bookings:
            self.factory.create(booking=booking, status=PaymentStatus.FAILED)

    @seed_actions
    def seed(self, rows: int = None) -> None:
        self._create_pending_payments()
        self._create_completed_payments()
        self._create_cancelled_payments()
        self._create_expired_payments()
