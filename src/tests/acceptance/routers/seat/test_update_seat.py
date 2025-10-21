from unittest.mock import ANY

from app.models import Seat
from tests.acceptance.routers.seat._base_seats_test import _TestBaseSeatEndpoints
from tests.common.factories.seat_factory import DisabledSeatFactory, EnabledSeatFactory


class TestUpdateSeatRouter(_TestBaseSeatEndpoints):
    def test_not_found(self):
        response = self.client.patch(url=f'{self.base_path}/99', json={}, exp_code=404)
        json_response = response.json()

        assert json_response
        assert json_response == {'detail': 'Seat not found'}

    def test_no_update_fields(self):
        seat = EnabledSeatFactory()
        current_seat = {'row': seat.row, 'number': seat.number, 'screen_id': seat.screen.id}

        response = self.client.patch(
            url=f'{self.base_path}/{seat.id}',
            json={},
        )

        assert response.json() == {
            'created_at': ANY,
            'id': seat.id,
            'inactive_at': None,
            'number': current_seat['number'],
            'row': current_seat['row'],
            'screen_id': current_seat['screen_id'],
            'updated_at': ANY,
        }

        with self.app.container.session() as session:
            found_seat = session.query(Seat).first()
            assert found_seat
            assert found_seat.id == seat.id
            assert found_seat.row == current_seat['row']
            assert found_seat.number == current_seat['number']
            assert found_seat.screen_id == current_seat['screen_id']

    def test_number_less_than_one(self):
        seat = EnabledSeatFactory()

        response = self.client.patch(url=f'{self.base_path}/{seat.id}', json={'number': 0}, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'ctx': {
                        'ge': 1,
                    },
                    'input': 0,
                    'loc': [
                        'body',
                        'number',
                    ],
                    'msg': 'Input should be greater than or equal to 1',
                    'type': 'greater_than_equal',
                },
            ],
        }

    def test_row_less_than_one(self):
        seat = EnabledSeatFactory()

        response = self.client.patch(url=f'{self.base_path}/{seat.id}', json={'row': 0}, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'ctx': {
                        'ge': 1,
                    },
                    'input': 0,
                    'loc': [
                        'body',
                        'row',
                    ],
                    'msg': 'Input should be greater than or equal to 1',
                    'type': 'greater_than_equal',
                },
            ],
        }

    def test_screen_not_found(self):
        seat = EnabledSeatFactory()

        response = self.client.patch(url=f'{self.base_path}/{seat.id}', json={'screen_id': 99}, exp_code=404)

        assert response.json() == {'detail': 'Screen not found'}

    def test_update_disabled_seat(self):
        seat = DisabledSeatFactory()

        response = self.client.patch(url=f'{self.base_path}/{seat.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Seat not found'}
