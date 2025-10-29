from sqlalchemy.orm import joinedload, Session
from sqlmodel import SQLModel

from app.models import Payment
from app.repositories import core


class PaymentRepository(
    core.AbstractCreateRepository,
    core.AbstractUpdateRepository,
    core.FindByIdMixin,
):
    def __init__(self, session: Session):
        super().__init__(model=Payment, session=session)

    def find_by_id(self, record_id: str) -> SQLModel | None:
        return self.session.query(Payment).options(joinedload(Payment.booking)).filter(Payment.id == record_id).first()

    def create(self, **kwargs) -> SQLModel:
        payment = self.model(**kwargs)
        self.session.add(payment)
        self.session.flush()
        return payment

    def update(self, record, **kwargs) -> SQLModel | None:
        for field, value in kwargs.items():
            setattr(record, field, value)

        return record
