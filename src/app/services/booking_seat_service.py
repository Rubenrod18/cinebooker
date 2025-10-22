from sqlmodel import Session

from app.models import BookingSeat
from app.repositories.booking_seat_repository import BookingSeatRepository
from app.services import core
from app.utils import financials


class BookingSeatService(
    core.AbstractCreateService,
    core.FindByIdMixin,
    core.GetMixin,
    core.AbstractUpdateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        booking_seat_repository: BookingSeatRepository | None = None,
    ):
        super().__init__(repository=booking_seat_repository or BookingSeatRepository(session))

    def create(self, **kwargs) -> BookingSeat:
        kwargs['price_with_vat'] = financials.apply_vat_rate(kwargs['base_price'], kwargs['vat_rate'])
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> BookingSeat:
        if 'base_price' in kwargs or 'vat_rate' in kwargs:
            base_price = kwargs.get('base_price', record.base_price)
            vat_rate = kwargs.get('vat_rate', record.vat_rate)
            kwargs['price_with_vat'] = financials.apply_vat_rate(base_price, vat_rate)
        return self.repository.update(record, **kwargs)
