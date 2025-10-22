from uuid import UUID

from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from app.models import Booking, BookingSeat
from app.models.booking import BookingStatus
from app.repositories import core


class BookingSeatRepository(
    core.AbstractCreateRepository,
    core.FindByIdMixin,
    core.AbstractUpdateRepository,
    core.GetMixin,
    core.FindOneMixin,
):
    def __init__(self, session: Session):
        super().__init__(model=BookingSeat, session=session)

    def create(self, **kwargs) -> BookingSeat:
        booking_seat = self.model(**kwargs)
        self.session.add(booking_seat)
        self.session.flush()
        return booking_seat

    def update(self, record, **kwargs) -> SQLModel | None:
        for field, value in kwargs.items():
            setattr(record, field, value)

        return record

    def find_pending_payment_by_id(self, record_id: int) -> SQLModel | None:
        with self.session as session:
            return (
                session.query(self.model)
                .outerjoin(Booking)
                .filter(
                    self.model.id == record_id,
                    Booking.status == BookingStatus.PENDING_PAYMENT.value,
                )
                .first()
            )

    def is_seat_available(self, showtime_id: UUID, seat_id: int) -> bool:
        with self.session as session:
            return (
                session.query(self.model)
                .outerjoin(Booking)
                .filter(
                    self.model.seat_id == seat_id,
                    Booking.showtime_id == showtime_id,
                    Booking.status == BookingStatus.CONFIRMED.value,
                )
                .first()
                is None
            )
