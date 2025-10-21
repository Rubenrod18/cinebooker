from datetime import date

from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, computed_field, ConfigDict, Field, field_validator, model_validator, PrivateAttr

from ..di_container import ServiceDIContainer
from ..exceptions import NotFoundException
from ..models import Customer
from ..repositories.customer_repository import CustomerRepository
from . import core
from .auth_schemas import AuthUserSchema


class CustomerCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    birth_date: date

    @model_validator(mode='after')
    def to_nested(self):
        return {
            'auth_user': {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'password': self.password,
            },
            'customer': {'birth_date': self.birth_date},
        }


# pylint: disable=no-member
class CustomerResponseSchema(core.CreatedUpdatedMixin, BaseModel):
    birth_date: date
    auth_user: AuthUserSchema = Field(..., exclude=True)

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    def first_name(self) -> str:
        return self.auth_user.first_name

    @computed_field
    def last_name(self) -> str:
        return self.auth_user.last_name

    @computed_field
    def email(self) -> str:
        return self.auth_user.email


class CustomerIdRequestSchema(BaseModel):
    customer_id: int
    _customer: Customer | None = PrivateAttr(default=None)

    @field_validator('customer_id')
    @classmethod
    @inject
    def validate_customer_id(
        cls, customer_id: int, customer_repository: CustomerRepository = Provide[ServiceDIContainer.customer_repository]
    ) -> int:
        customer = customer_repository.find_by_id(customer_id)

        if not customer:
            raise NotFoundException(description='Customer not found')

        cls._customer = customer
        return customer_id

    @property
    def customer(self) -> Customer:
        return self._customer
