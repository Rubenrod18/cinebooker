from datetime import datetime, timedelta

import pytest

from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.screen._base_screens_test import _TestBaseScreenEndpoints
from tests.common.factories.screen_factory import DisabledScreenFactory, EnabledScreenFactory


class TestListScreenRouter(_TestBaseScreenEndpoints):
    def test_list_screens(self):
        current_dt = datetime.now()
        screen = EnabledScreenFactory(created_at=current_dt - timedelta(days=1))
        screen_2 = EnabledScreenFactory(created_at=current_dt)
        DisabledScreenFactory(created_at=current_dt)
        screens = [screen, screen_2]

        response = self.client.get(url=self.base_path)
        json_response = response.json()

        assert json_response
        assert len(json_response) == len(screens)

        for i, screen in enumerate(json_response):
            assert screen['name'] == str(screens[i].name)
            assert screen['capacity'] == screens[i].capacity
            assert screen['created_at'] == screens[i].created_at.strftime(DEFAULT_DATETIME_FORMAT)
            assert screen['updated_at'] == screens[i].updated_at.strftime(DEFAULT_DATETIME_FORMAT)

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_screens',
        [
            (1, 3, 3),
            (2, 3, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_screens_found_filter_by_page_number(self, page_number, items_per_page, total_expected_screens):
        [EnabledScreenFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_screens

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_screens',
        [
            (1, 1, 1),
            (4, 1, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_screens_found_filter_by_items_per_page(self, page_number, items_per_page, total_expected_screens):
        [EnabledScreenFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_screens
