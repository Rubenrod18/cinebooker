from sqlmodel import Session

from app.models import InvoiceItem
from app.repositories.invoice_item_repository import InvoiceItemRepository
from app.services import core


class InvoiceItemService(
    core.AbstractBaseService,
    core.AbstractCreateService,
    core.AbstractDeleteService,
    core.AbstractUpdateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        invoice_item_repository: InvoiceItemRepository | None = None,
    ):
        super().__init__(repository=invoice_item_repository or InvoiceItemRepository(session))

    def create(self, **kwargs) -> InvoiceItem:
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> InvoiceItem:
        return self.repository.update(record, **kwargs)

    def delete(self, record, **kwargs) -> None:
        self.repository.delete(record, **kwargs)
