from datetime import date

from pydantic import BaseModel, computed_field, ConfigDict, Field, model_validator

from . import core
from .auth_schemas import AuthUserSchema


class CustomerCreateFields(BaseModel):
    birth_date: date


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
