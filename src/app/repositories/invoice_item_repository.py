from sqlalchemy.orm import Session

from app.models import InvoiceItem
from app.repositories import core


class InvoiceItemRepository(
    core.AbstractBaseRepository,
    core.AbstractCreateRepository,
):
    def __init__(self, session: Session):
        super().__init__(model=InvoiceItem, session=session)

    def create(self, **kwargs) -> InvoiceItem:
        invoice_item = self.model(**kwargs)
        self.session.add(invoice_item)
        self.session.flush()
        return invoice_item
