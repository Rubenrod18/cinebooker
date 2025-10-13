from datetime import datetime, timedelta

import pytest

from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.discount._base_discounts_test import _TestBaseDiscountEndpoints
from tests.common.factories.discount_factory import DisabledDiscountFactory, EnabledDiscountFactory


class TestListDiscountRouter(_TestBaseDiscountEndpoints):
    def test_list_discounts(self):
        current_dt = datetime.now()
        discount = EnabledDiscountFactory(created_at=current_dt - timedelta(days=1), expires_at=None)
        discount_2 = EnabledDiscountFactory(created_at=current_dt, expires_at=None)
        DisabledDiscountFactory(created_at=current_dt, expires_at=None)
        discounts = [discount, discount_2]

        response = self.client.get(url=self.base_path)
        json_response = response.json()

        assert json_response
        assert len(json_response) == len(discounts)

        for i, discount in enumerate(json_response):
            assert discount['code'] == str(discounts[i].code)
            assert discount['description'] == discounts[i].description
            assert discount['is_percentage'] is discounts[i].is_percentage
            assert str(discount['amount']) == str(discounts[i].amount)
            assert discount['expires_at'] is None
            assert discount['usage_limit'] == discounts[i].usage_limit
            assert discount['times_used'] == discounts[i].times_used
            assert discount['created_at'] == discounts[i].created_at.strftime(DEFAULT_DATETIME_FORMAT)
            assert discount['updated_at'] == discounts[i].updated_at.strftime(DEFAULT_DATETIME_FORMAT)

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_discount',
        [
            (1, 3, 3),
            (2, 3, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_discounts_found_filter_by_page_number(self, page_number, items_per_page, total_expected_discount):
        [EnabledDiscountFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_discount

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_discount',
        [
            (1, 1, 1),
            (4, 1, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_discounts_found_filter_by_items_per_page(self, page_number, items_per_page, total_expected_discount):
        [EnabledDiscountFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_discount
