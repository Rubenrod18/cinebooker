import secrets
import string

from iso4217 import Currency
from sqlmodel import Session

from app.models import Invoice
from app.models.invoice import InvoiceStatus
from app.repositories.invoice_repository import InvoiceRepository
from app.services import core


class InvoiceService(
    core.AbstractBaseService,
    core.AbstractCreateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        invoice_repository: InvoiceRepository | None = None,
    ):
        super().__init__(repository=invoice_repository or InvoiceRepository(session))

    def generate_unique_locator(self, length: int | None = None):
        length = length or 13

        while True:
            locator = ''.join(secrets.choice(string.digits) for _ in range(length))

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
