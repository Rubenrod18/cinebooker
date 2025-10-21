from sqlalchemy.orm import Session

from app.models import Customer
from app.repositories import core


class CustomerRepository(
    core.AbstractCreateRepository,
    core.FindByIdMixin,
):
    def __init__(self, session: Session):
        super().__init__(model=Customer, session=session)

    def create(self, **kwargs) -> Customer:
        customer = self.model(**kwargs)
        self.session.add(customer)
        self.session.flush()
        return customer
