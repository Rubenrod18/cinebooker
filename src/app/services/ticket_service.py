from sqlmodel import Session

from app.models import Ticket
from app.models.ticket import TicketBarcodeType, TicketStatus
from app.repositories.ticket_repository import TicketRepository
from app.services import core
from app.utils import generate_unique_code


class TicketService(
    core.AbstractBaseService,
    core.AbstractCreateService,
    core.AbstractUpdateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        ticket_repository: TicketRepository | None = None,
    ):
        super().__init__(repository=ticket_repository or TicketRepository(session))

    def _generate_unique_barcode(self, length: int, letters: bool = True):
        while True:
            barcode_value = generate_unique_code(length, letters)

            if not self.repository.find_by_barcode_value(barcode_value):
                return barcode_value

    def create(self, **kwargs) -> Ticket:
        kwargs.update(
            {
                # HACK: Import settings.BARCODE_LENGTH here instead of 30. Fix circular import problem
                'barcode_value': self._generate_unique_barcode(length=30, letters=True),
                'barcode_type': TicketBarcodeType.QR,
                'status': TicketStatus.ISSUED,
            }
        )
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> Ticket:
        return self.repository.update(record, **kwargs)
