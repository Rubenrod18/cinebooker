from datetime import datetime, timedelta

import pytest

from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.booking_seat._base_booking_seats_test import _TestBaseBookingSeatEndpoints
from tests.common.factories.booking_factory import (
    CancelledBookingSeatFactory,
    ConfirmedBookingSeatFactory,
    ExpiredBookingSeatFactory,
    PendingPaymentBookingSeatFactory,
)


class TestListBookingSeatRouter(_TestBaseBookingSeatEndpoints):
    def test_list_booking_seats(self):
        current_dt = datetime.now()
        booking_seat = ConfirmedBookingSeatFactory(created_at=current_dt - timedelta(days=1))
        booking_seat_2 = PendingPaymentBookingSeatFactory(created_at=current_dt)
        booking_seat_3 = ExpiredBookingSeatFactory(created_at=current_dt)
        booking_seat_4 = CancelledBookingSeatFactory(created_at=current_dt)
        booking_seats = [booking_seat, booking_seat_2, booking_seat_3, booking_seat_4]

        response = self.client.get(url=self.base_path)
        json_response = response.json()

        assert json_response
        assert len(json_response) == len(booking_seats)

        for i, booking_seat in enumerate(json_response):
            assert booking_seat == {
                'id': booking_seats[i].id,
                'booking_id': str(booking_seats[i].booking_id),
                'seat_id': booking_seats[i].seat_id,
                'created_at': booking_seats[i].created_at.strftime(DEFAULT_DATETIME_FORMAT),
                'updated_at': booking_seats[i].updated_at.strftime(DEFAULT_DATETIME_FORMAT),
                'base_price': str(booking_seats[i].base_price),
                'vat_rate': str(booking_seats[i].vat_rate),
                'price_with_vat': str(booking_seats[i].price_with_vat),
            }

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_booking_seats',
        [
            (1, 3, 3),
            (2, 3, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_booking_seats_found_filter_by_page_number(
        self, page_number, items_per_page, total_expected_booking_seats
    ):
        [ConfirmedBookingSeatFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_booking_seats

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_booking_seats',
        [
            (1, 1, 1),
            (4, 1, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_booking_seats_found_filter_by_items_per_page(
        self, page_number, items_per_page, total_expected_booking_seats
    ):
        [ConfirmedBookingSeatFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_booking_seats
