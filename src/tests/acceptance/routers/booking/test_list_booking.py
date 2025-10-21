from datetime import datetime, timedelta

import pytest

from tests.acceptance.routers.booking._base_booking_test import _TestBaseBookingEndpoints
from tests.common.factories.booking_factory import EnabledBookingFactory, ExpiredBookingFactory


class TestListBookingRouter(_TestBaseBookingEndpoints):
    def test_list_bookings(self):
        current_dt = datetime.now()
        booking = EnabledBookingFactory(created_at=current_dt - timedelta(days=1))
        booking_2 = EnabledBookingFactory(created_at=current_dt)
        ExpiredBookingFactory(created_at=current_dt)
        bookings = [booking, booking_2]

        response = self.client.get(url=self.base_path)
        json_response = response.json()

        assert json_response
        assert len(json_response) == len(bookings)

        for i, booking in enumerate(json_response):
            assert booking['customer_id'] == bookings[i].customer_id
            assert booking['showtime_id'] == str(bookings[i].showtime_id)
            assert booking['discount_id'] == bookings[i].discount_id
            assert booking['status'] == bookings[i].status
            assert booking['expired_at'] is None

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_bookings',
        [
            (1, 3, 3),
            (2, 3, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_bookings_found_filter_by_page_number(self, page_number, items_per_page, total_expected_bookings):
        [EnabledBookingFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_bookings

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_bookings',
        [
            (1, 1, 1),
            (4, 1, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_bookings_found_filter_by_items_per_page(self, page_number, items_per_page, total_expected_bookings):
        [EnabledBookingFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_bookings
