import random

from app.models import Discount
from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.discount._base_discounts_test import _TestBaseDiscountEndpoints
from tests.common.factories.discount_factory import EnabledDiscountFactory


class TestCreateDiscountEndpoint(_TestBaseDiscountEndpoints):
    def test_create_discount(self):
        payload = {
            'code': self.faker.unique.bothify(text='DISCOUNT-####'),
            'description': self.faker.sentence(nb_words=5),
            'is_percentage': self.faker.boolean(),
            'amount': str(round(random.uniform(5, 50), 2)),
            'expires_at': (
                self.faker.date_time_between(start_date='now', end_date='+90d').strftime(DEFAULT_DATETIME_FORMAT)
                if self.faker.boolean()
                else None
            ),
            'usage_limit': random.choice([None, random.randint(10, 100)]),
        }

        response = self.client.post(url=self.base_path, json=payload)
        json_response = response.json()

        assert json_response
        assert json_response['code'] == payload['code']
        assert json_response['description'] == payload['description']
        assert json_response['is_percentage'] is payload['is_percentage']
        assert str(json_response['amount']) == payload['amount']
        assert json_response['expires_at'] == payload['expires_at']
        assert json_response['usage_limit'] == payload['usage_limit']
        if payload['usage_limit']:
            assert json_response['times_used'] == 0
        else:
            assert json_response['times_used'] is None

        with self.app.container.session() as session:
            discount = session.query(Discount).first()
            assert discount
            assert discount.code == payload['code']
            assert discount.description == payload['description']
            assert discount.is_percentage is payload['is_percentage']
            assert str(discount.amount) == payload['amount']
            assert (
                discount.expires_at.strftime(DEFAULT_DATETIME_FORMAT)
                if discount.expires_at
                else discount.expires_at == payload['expires_at']
            )
            assert discount.usage_limit == payload['usage_limit']
            if payload['usage_limit']:
                assert discount.times_used == 0
            else:
                assert discount.times_used is None

    def test_amount_less_than_zero(self):
        payload = {
            'code': self.faker.unique.bothify(text='DISCOUNT-####'),
            'description': self.faker.sentence(nb_words=5),
            'is_percentage': self.faker.boolean(),
            'amount': str(-1),
            'expires_at': (
                self.faker.date_time_between(start_date='now', end_date='+90d').strftime(DEFAULT_DATETIME_FORMAT)
                if self.faker.boolean()
                else None
            ),
            'usage_limit': random.choice([None, random.randint(10, 100)]),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'type': 'greater_than_equal',
                    'loc': ['body', 'amount'],
                    'msg': 'Input should be greater than or equal to 1',
                    'input': '-1',
                    'ctx': {'ge': 1},
                }
            ]
        }

    def test_usage_limit_less_than_zero(self):
        payload = {
            'code': self.faker.unique.bothify(text='DISCOUNT-####'),
            'description': self.faker.sentence(nb_words=5),
            'is_percentage': self.faker.boolean(),
            'amount': str(round(random.uniform(5, 50), 2)),
            'expires_at': (
                self.faker.date_time_between(start_date='now', end_date='+90d').strftime(DEFAULT_DATETIME_FORMAT)
                if self.faker.boolean()
                else None
            ),
            'usage_limit': -1,
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'type': 'greater_than_equal',
                    'loc': ['body', 'usage_limit'],
                    'msg': 'Input should be greater than or equal to 1',
                    'input': -1,
                    'ctx': {'ge': 1},
                }
            ]
        }

    def test_expires_at_less_than_current_datetime(self):
        payload = {
            'code': self.faker.unique.bothify(text='DISCOUNT-####'),
            'description': self.faker.sentence(nb_words=5),
            'is_percentage': self.faker.boolean(),
            'amount': str(round(random.uniform(5, 50), 2)),
            'expires_at': (
                self.faker.date_time_between(start_date='-7d', end_date='-1d').strftime(DEFAULT_DATETIME_FORMAT)
            ),
            'usage_limit': random.randint(10, 100),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {'detail': 'Must be greater than or equal to the current datetime'}

    def test_discount_code_already_exists(self):
        discount = EnabledDiscountFactory()
        payload = {
            'code': discount.code,
            'description': self.faker.sentence(nb_words=5),
            'is_percentage': self.faker.boolean(),
            'amount': str(round(random.uniform(5, 50), 2)),
            'expires_at': (
                self.faker.date_time_between(start_date='now', end_date='+90d').strftime(DEFAULT_DATETIME_FORMAT)
                if self.faker.boolean()
                else None
            ),
            'usage_limit': random.choice([None, random.randint(10, 100)]),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {'detail': 'code already exists'}
