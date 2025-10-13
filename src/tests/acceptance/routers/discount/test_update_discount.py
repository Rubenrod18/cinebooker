from app.models import Discount
from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.discount._base_discounts_test import _TestBaseDiscountEndpoints
from tests.common.factories.discount_factory import DisabledDiscountFactory, EnabledDiscountFactory


class TestUpdateDiscountRouter(_TestBaseDiscountEndpoints):
    def test_not_found(self):
        response = self.client.patch(url=f'{self.base_path}/99', json={}, exp_code=404)
        json_response = response.json()

        assert json_response
        assert json_response == {'detail': 'Discount not found'}

    def test_no_update_fields(self):
        discount = EnabledDiscountFactory()
        current_discount = {
            'code': discount.code,
            'description': discount.description,
            'is_percentage': discount.is_percentage,
            'amount': str(discount.amount),
            'expires_at': discount.expires_at,
            'usage_limit': discount.usage_limit,
            'times_used': discount.times_used,
        }

        response = self.client.patch(
            url=f'{self.base_path}/{discount.code}',
            json={},
        )
        json_response = response.json()

        assert json_response
        assert json_response['code'] == current_discount['code']
        assert json_response['description'] == current_discount['description']
        assert json_response['is_percentage'] is current_discount['is_percentage']
        assert str(json_response['amount']) == current_discount['amount']
        assert json_response['expires_at'] == current_discount['expires_at']
        assert json_response['times_used'] == current_discount['times_used']

        with self.app.container.session() as session:
            found_discount = session.query(Discount).first()
            assert found_discount
            assert found_discount.code == current_discount['code']
            assert found_discount.description == current_discount['description']
            assert found_discount.is_percentage is current_discount['is_percentage']
            assert str(found_discount.amount) == current_discount['amount']
            assert found_discount.expires_at == current_discount['expires_at']
            assert found_discount.usage_limit == current_discount['usage_limit']
            assert found_discount.times_used == current_discount['times_used']

    def test_amount_less_than_zero(self):
        discount = EnabledDiscountFactory()
        payload = {'amount': str(-1)}

        response = self.client.patch(url=f'{self.base_path}/{discount.code}', json=payload, exp_code=422)

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
        discount = EnabledDiscountFactory()
        payload = {'usage_limit': -1}

        response = self.client.patch(url=f'{self.base_path}/{discount.code}', json=payload, exp_code=422)

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
        discount = EnabledDiscountFactory()
        payload = {
            'expires_at': (
                self.faker.date_time_between(start_date='-7d', end_date='-1d').strftime(DEFAULT_DATETIME_FORMAT)
            )
        }

        response = self.client.patch(url=f'{self.base_path}/{discount.code}', json=payload, exp_code=422)

        assert response.json() == {'detail': 'Must be greater than or equal to the current datetime'}

    def test_update_disabled_discount(self):
        Discount = DisabledDiscountFactory()

        response = self.client.patch(url=f'{self.base_path}/{Discount.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Discount not found'}
