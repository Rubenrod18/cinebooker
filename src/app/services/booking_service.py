from sqlmodel import Session

from app.models import Booking
from app.models.booking import BookingStatus
from app.repositories.booking_repository import BookingRepository
from app.services import core


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
    ):
        super().__init__(repository=booking_repository or BookingRepository(session))

    def create(self, **kwargs) -> Booking:
        kwargs['status'] = BookingStatus.PENDING_PAYMENT
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> Booking:
        return self.repository.update(record, **kwargs)
