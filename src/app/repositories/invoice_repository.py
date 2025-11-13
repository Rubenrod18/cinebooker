from sqlalchemy.orm import Session

from app.models import Invoice
from app.repositories import core


class InvoiceRepository(
    core.AbstractCreateRepository,
    core.FindOneMixin,
):
    def __init__(self, session: Session):
        super().__init__(model=Invoice, session=session)

    def create(self, **kwargs) -> Invoice:
        invoice = self.model(**kwargs)
        self.session.add(invoice)
        self.session.flush()
        return invoice

    def find_by_code(self, code: str) -> Invoice:
        return self.find_one(code=code)
