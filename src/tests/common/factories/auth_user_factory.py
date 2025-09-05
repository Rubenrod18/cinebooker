import os
import random
import uuid
from datetime import timedelta

import factory

from app.helpers.password_handler import PasswordHandler
from app.models import AuthUser

from ...conftest import faker
from .base_factory import BaseFactory


class AuthUserFactory(BaseFactory):
    class Meta:
        model = AuthUser

    first_name = factory.Faker('name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: f'user_email_{uuid.uuid4().hex}@mail.com')

    @factory.lazy_attribute
    def password(self):
        return PasswordHandler.ensure_password(os.getenv('TEST_USER_PASSWORD'))

    @factory.lazy_attribute
    def date_joined(self):
        return faker.date_time_between(start_date='-3y', end_date='now')

    @factory.lazy_attribute
    def last_login(self):
        return self.date_joined + timedelta(days=1)

    @factory.lazy_attribute
    def inactive_at(self):
        return random.choice([self.date_joined + timedelta(days=2), None])
