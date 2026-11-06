import factory

from app.models import Customer

from .auth_user_factory import AuthUserFactory, EnabledAuthUserFactory
from .base_factory import BaseFactory


class CustomerFactory(BaseFactory):
    class Meta:
        model = Customer

    birth_date = factory.Faker('date_between', start_date='-30y', end_date='-5y')
    auth_user = factory.SubFactory(AuthUserFactory)


class EnabledCustomerFactory(CustomerFactory):
    auth_user = factory.SubFactory(EnabledAuthUserFactory)
