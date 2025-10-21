from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.seat._base_seats_test import _TestBaseSeatEndpoints
from tests.common.factories.seat_factory import DisabledSeatFactory, EnabledSeatFactory


class TestGetSeatRouter(_TestBaseSeatEndpoints):
    def test_not_found(self):
        response = self.client.get(url=f'{self.base_path}/99', json={}, exp_code=404)

        assert response.json() == {'detail': 'Seat not found'}

    def test_find_by_id_disabled_seat(self):
        seat = DisabledSeatFactory()

        response = self.client.get(url=f'{self.base_path}/{seat.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Seat not found'}

    def test_find_by_id_enabled_seat(self):
        seat = EnabledSeatFactory()

        response = self.client.get(url=f'{self.base_path}/{seat.id}', json={})

        assert response.json() == {
            'number': seat.number,
            'created_at': seat.created_at.strftime(DEFAULT_DATETIME_FORMAT),
            'id': seat.id,
            'inactive_at': None,
            'row': seat.row,
            'screen_id': seat.screen.id,
            'updated_at': seat.updated_at.strftime(DEFAULT_DATETIME_FORMAT),
        }
