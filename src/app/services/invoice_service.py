from iso4217 import Currency
from sqlmodel import Session

from app.models import Invoice
from app.models.invoice import InvoiceStatus
from app.repositories.invoice_repository import InvoiceRepository
from app.services import core
from app.utils import generate_unique_code


class InvoiceService(
    core.AbstractBaseService,
    core.AbstractCreateService,
    core.AbstractUpdateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        invoice_repository: InvoiceRepository | None = None,
    ):
        super().__init__(repository=invoice_repository or InvoiceRepository(session))

    def generate_unique_locator(self, length: int | None = None):
        while True:
            locator = generate_unique_code(length)

            if not self.repository.find_by_code(locator):
                return locator

    def create(self, **kwargs) -> Invoice:
        kwargs.update(
            {
                'code': self.generate_unique_locator(),
                'currency': kwargs.get('currency', Currency.EUR.value),  # pylint: disable=no-member
                'status': InvoiceStatus.ISSUED,
            }
        )
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> Invoice:
        return self.repository.update(record, **kwargs)

    def paid(self, record, **kwargs) -> Invoice:
        kwargs['status'] = InvoiceStatus.PAID
        return self.update(record, **kwargs)
