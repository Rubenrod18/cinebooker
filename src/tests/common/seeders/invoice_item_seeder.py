import sqlalchemy as sa

from app.models import Invoice

from ..factories.invoice_factory import InvoiceItemFactory
from . import seed_actions
from .core import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='InvoiceItemSeeder', priority=9, factory=InvoiceItemFactory)
        self._session = self.factory.get_db_session()

    def _create_invoice_items(self):
        invoices = self._session.query(Invoice).order_by(sa.func.random()).all()

        for invoice in invoices:
            self.factory.create(invoice=invoice)

    @seed_actions
    def seed(self, rows: int = None) -> None:
        self._create_invoice_items()
