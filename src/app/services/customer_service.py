from sqlmodel import Session

from app.models import Customer
from app.repositories.customer_repository import CustomerRepository
from app.services import core


class CustomerService(
    core.AbstractBaseService,
    core.AbstractCreateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        customer_repository: CustomerRepository | None = None,
    ):
        super().__init__(repository=customer_repository or CustomerRepository(session))

    def create(self, **kwargs) -> Customer:
        return self.repository.create(**kwargs)
