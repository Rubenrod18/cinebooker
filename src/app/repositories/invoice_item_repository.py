from sqlalchemy.orm import Session

from app.models import InvoiceItem
from app.repositories import core


class InvoiceItemRepository(
    core.AbstractBaseRepository,
    core.AbstractCreateRepository,
    core.AbstractDeleteRepository,
    core.AbstractUpdateRepository,
):
    def __init__(self, session: Session):
        super().__init__(model=InvoiceItem, session=session)

    def create(self, **kwargs) -> InvoiceItem:
        invoice_item = self.model(**kwargs)
        self.session.add(invoice_item)
        self.session.flush()
        return invoice_item

    def update(self, record, **kwargs) -> InvoiceItem | None:
        for field, value in kwargs.items():
            setattr(record, field, value)

        return record

    def delete(self, record, **kwargs) -> InvoiceItem | None:
        self.session.delete(record)
        return record
