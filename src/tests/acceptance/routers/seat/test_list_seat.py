from datetime import datetime, timedelta

import pytest

from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.seat._base_seats_test import _TestBaseSeatEndpoints
from tests.common.factories.seat_factory import DisabledSeatFactory, EnabledSeatFactory


class TestListSeatRouter(_TestBaseSeatEndpoints):
    def test_list_seats(self):
        current_dt = datetime.now()
        seat = EnabledSeatFactory(created_at=current_dt - timedelta(days=1))
        seat_2 = EnabledSeatFactory(created_at=current_dt)
        DisabledSeatFactory(created_at=current_dt)
        seats = [seat, seat_2]

        response = self.client.get(url=self.base_path)
        json_response = response.json()

        assert json_response == [
            {
                'number': seat.number,
                'created_at': seat.created_at.strftime(DEFAULT_DATETIME_FORMAT),
                'id': seat.id,
                'inactive_at': None,
                'row': seat.row,
                'screen_id': seat.screen.id,
                'updated_at': seat.updated_at.strftime(DEFAULT_DATETIME_FORMAT),
            },
            {
                'number': seat_2.number,
                'created_at': seat_2.created_at.strftime(DEFAULT_DATETIME_FORMAT),
                'id': seat_2.id,
                'inactive_at': None,
                'row': seat_2.row,
                'screen_id': seat_2.screen.id,
                'updated_at': seat_2.updated_at.strftime(DEFAULT_DATETIME_FORMAT),
            },
        ]

        for i, seat in enumerate(json_response):
            assert seat['number'] == seats[i].number
            assert seat['row'] == seats[i].row
            assert seat['screen_id'] == seats[i].screen_id
            assert seat['created_at'] == seats[i].created_at.strftime(DEFAULT_DATETIME_FORMAT)
            assert seat['updated_at'] == seats[i].updated_at.strftime(DEFAULT_DATETIME_FORMAT)

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_seats',
        [
            (1, 3, 3),
            (2, 3, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_seats_found_filter_by_page_number(self, page_number, items_per_page, total_expected_seats):
        [EnabledSeatFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_seats

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_seats',
        [
            (1, 1, 1),
            (4, 1, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_seats_found_filter_by_items_per_page(self, page_number, items_per_page, total_expected_seats):
        [EnabledSeatFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_seats
