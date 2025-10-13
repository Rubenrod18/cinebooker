from app.models import Discount
from tests.acceptance.routers.discount._base_discounts_test import _TestBaseDiscountEndpoints
from tests.common.factories.discount_factory import DisabledDiscountFactory, EnabledDiscountFactory


class TestDeleteDiscountRouter(_TestBaseDiscountEndpoints):
    def test_not_found(self):
        response = self.client.delete(url=f'{self.base_path}/fake_code', json={}, exp_code=404)

        assert response.json() == {'detail': 'Discount not found'}

    def test_delete_disabled_discount(self):
        discount = DisabledDiscountFactory()

        response = self.client.delete(url=f'{self.base_path}/{discount.code}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Discount not found'}

    def test_delete_enabled_discount(self):
        discount = EnabledDiscountFactory()

        self.client.delete(url=f'{self.base_path}/{discount.code}', json={}, exp_code=204)

        with self.app.container.session() as session:
            found_discount = session.query(Discount).first()
            assert found_discount
            assert found_discount.id == discount.id
            assert found_discount.is_inactived
