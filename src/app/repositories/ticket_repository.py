from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from app.models import Ticket
from app.repositories import core


class TicketRepository(
    core.AbstractCreateRepository,
    core.AbstractUpdateRepository,
    core.FindOneMixin,
):
    def __init__(self, session: Session):
        super().__init__(model=Ticket, session=session)

    def create(self, **kwargs) -> Ticket:
        ticket = self.model(**kwargs)
        self.session.add(ticket)
        self.session.flush()
        return ticket

    def update(self, record, **kwargs) -> SQLModel | None:
        for field, value in kwargs.items():
            setattr(record, field, value)

        return record

    def find_by_barcode_value(self, barcode_value: str) -> SQLModel | None:
        return self.find_one(filter_by={'barcode_value': barcode_value})
