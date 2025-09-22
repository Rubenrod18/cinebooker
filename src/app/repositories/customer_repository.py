from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy.orm import Session

from app.models import Customer
from app.repositories import core


class CustomerRepository(
    core.AbstractBaseRepository,
    core.AbstractCreateRepository,
):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        super().__init__(model=Customer, session=session)

    def create(self, **kwargs) -> Customer:
        # auto_flush = kwargs.pop('auto_flush', True)
        customer = self.model(**kwargs)
        self.session.add(customer)
        self.session.flush()
        return customer
