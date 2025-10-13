from datetime import datetime, timedelta

import pytest

from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.showtime._base_showtime_test import _TestBaseShowtimeEndpoints
from tests.common.factories.showtime_factory import ShowtimeFactory


class TestListShowtimeRouter(_TestBaseShowtimeEndpoints):
    def test_list_showtimes(self):
        current_dt = datetime.now()
        showtime = ShowtimeFactory(created_at=current_dt - timedelta(days=1))
        showtime_2 = ShowtimeFactory(created_at=current_dt)
        showtimes = [showtime, showtime_2]

        response = self.client.get(url=self.base_path)
        json_response = response.json()

        assert json_response
        assert len(json_response) == len(showtimes)

        for i, showtime in enumerate(json_response):
            assert showtime['movie_id'] == showtimes[i].movie_id
            assert showtime['screen_id'] == showtimes[i].screen_id
            assert showtime['start_time'] == showtimes[i].start_time.strftime(DEFAULT_DATETIME_FORMAT)
            assert showtime['base_price'] == str(showtimes[i].base_price)
            assert showtime['vat_rate'] == str(showtimes[i].vat_rate)
            assert showtime['price_with_vat'] == str(showtimes[i].price_with_vat)

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_showtimes',
        [
            (1, 3, 3),
            (2, 3, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_showtimes_found_filter_by_page_number(self, page_number, items_per_page, total_expected_showtimes):
        [ShowtimeFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_showtimes

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_showtimes',
        [
            (1, 1, 1),
            (4, 1, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_showtimes_found_filter_by_items_per_page(self, page_number, items_per_page, total_expected_showtimes):
        [ShowtimeFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_showtimes
