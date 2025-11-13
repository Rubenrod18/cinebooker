from sqlmodel import Session

from app.models import InvoiceItem
from app.repositories.invoice_item_repository import InvoiceItemRepository
from app.services import core


class InvoiceItemService(
    core.AbstractBaseService,
    core.AbstractCreateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        invoice_item_repository: InvoiceItemRepository | None = None,
    ):
        super().__init__(repository=invoice_item_repository or InvoiceItemRepository(session))

    def create(self, **kwargs) -> InvoiceItem:
        return self.repository.create(**kwargs)
