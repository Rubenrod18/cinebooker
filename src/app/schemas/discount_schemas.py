from datetime import date, datetime, UTC
from decimal import Decimal

from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, PrivateAttr

from ..di_container import ServiceDIContainer
from ..exceptions import NotFoundException, UnprocessableEntityException
from ..models import Discount
from ..repositories.discount_repository import DiscountRepository
from . import core


class DiscountCreateSchema(BaseModel):
    code: str
    description: str
    is_percentage: bool
    amount: Decimal = Field(None, ge=1)
    expires_at: date | None = None
    usage_limit: int | None = Field(None, ge=1)
    times_used: int | None = None

    @field_validator('code')
    @classmethod
    @inject
    def validate_code(
        cls, code: str, discount_repository: DiscountRepository = Provide[ServiceDIContainer.discount_repository]
    ) -> str:
        if discount_repository.find_by_code(code):
            raise UnprocessableEntityException(description='code already exists')

        return code

    @field_validator('expires_at')
    @classmethod
    def validate_expires_at(cls, value: date) -> date | None:
        if isinstance(value, date):
            now = datetime.now(UTC).date()
            if value < now:
                raise UnprocessableEntityException(description='Must be greater than or equal to the current datetime')
        return value

    @model_validator(mode='after')
    def initial_times_used(self):
        if isinstance(self.usage_limit, int):
            self.times_used = 0

        return self


class DiscountUpdateSchema(BaseModel):
    description: str | None = None
    is_percentage: bool | None = None
    amount: Decimal = Field(None, ge=1)
    expires_at: date | None = None
    usage_limit: int | None = Field(None, ge=1)
    times_used: int | None = None

    @field_validator('expires_at')
    @classmethod
    def validate_expires_at(cls, value: date) -> date | None:
        if isinstance(value, date):
            now = datetime.now(UTC).date()
            if value < now:
                raise UnprocessableEntityException(description='Must be greater than or equal to the current datetime')
        return value

    @model_validator(mode='after')
    def check_usage_limit_and_times_used(self):
        if (
            isinstance(self.usage_limit, int) and isinstance(self.times_used, int)
        ) and self.usage_limit < self.times_used:
            raise UnprocessableEntityException(description='usage_limit cannot be less than times_used')

        return self


class DiscountResponseSchema(core.IntegerPKMixin, core.CreatedUpdatedMixin, core.InactiveMixin, BaseModel):
    code: str
    description: str
    is_percentage: bool
    amount: Decimal
    expires_at: date | None = None
    usage_limit: int | None = None
    times_used: int | None = None

    model_config = ConfigDict(from_attributes=True)


class DiscountCodeRequestSchema(BaseModel):
    discount_code: str
    _discount: Discount | None = PrivateAttr(default=None)

    @field_validator('discount_code')
    @classmethod
    @inject
    def validate_discount_code(
        cls,
        discount_code: str,
        discount_repository: DiscountRepository = Provide[ServiceDIContainer.discount_repository],
    ) -> str:
        discount = discount_repository.find_by_code(discount_code)

        if not discount:
            raise NotFoundException(description='Discount not found')

        cls._discount = discount
        return discount_code

    @property
    def discount(self) -> Discount:
        return self._discount
