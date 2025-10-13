from tests.acceptance.routers.discount._base_discounts_test import _TestBaseDiscountEndpoints
from tests.common.factories.discount_factory import DisabledDiscountFactory, EnabledDiscountFactory


class TestGetDiscountRouter(_TestBaseDiscountEndpoints):
    def test_not_found(self):
        response = self.client.get(url=f'{self.base_path}/fake_code', json={}, exp_code=404)

        assert response.json() == {'detail': 'Discount not found'}

    def test_find_by_id_disabled_Discount(self):
        discount = DisabledDiscountFactory()

        response = self.client.get(url=f'{self.base_path}/{discount.code}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Discount not found'}

    def test_find_by_id_enabled_Discount(self):
        discount = EnabledDiscountFactory(expires_at=None)

        response = self.client.get(url=f'{self.base_path}/{discount.code}', json={})
        json_response = response.json()

        assert json_response
        assert json_response['code'] == discount.code
        assert json_response['description'] == discount.description
        assert json_response['is_percentage'] == discount.is_percentage
        assert json_response['amount'] == str(discount.amount)
        assert json_response['expires_at'] is None
        assert json_response['usage_limit'] == discount.usage_limit
        assert json_response['times_used'] == discount.times_used
