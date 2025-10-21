from unittest.mock import ANY

from app.models import Seat
from tests.acceptance.routers.seat._base_seats_test import _TestBaseSeatEndpoints
from tests.common.factories.screen_factory import DisabledScreenFactory, EnabledScreenFactory


class TestCreateSeatEndpoint(_TestBaseSeatEndpoints):
    def test_create_seat(self):
        screen = EnabledScreenFactory()
        payload = {
            'screen_id': screen.id,
            'number': self.faker.random_int(1, 200),
            'row': self.faker.random_int(1, 200),
        }

        response = self.client.post(url=self.base_path, json=payload)

        assert response.json() == {
            'created_at': ANY,
            'id': 1,
            'inactive_at': None,
            'number': payload['number'],
            'row': payload['row'],
            'screen_id': payload['screen_id'],
            'updated_at': ANY,
        }

        with self.app.container.session() as session:
            seat = session.query(Seat).first()
            assert seat
            assert seat.screen_id == payload['screen_id']
            assert seat.number == payload['number']
            assert seat.row == payload['row']
            assert seat.is_actived

    def test_number_less_than_one(self):
        screen = EnabledScreenFactory()
        payload = {
            'screen_id': screen.id,
            'number': 0,
            'row': self.faker.random_int(1, 200),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

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
        screen = EnabledScreenFactory()
        payload = {
            'screen_id': screen.id,
            'number': self.faker.random_int(1, 200),
            'row': 0,
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

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
        payload = {
            'screen_id': 99,
            'number': self.faker.random_int(1, 200),
            'row': self.faker.random_int(1, 200),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Screen not found'}

    def test_disabled_screen_not_found(self):
        screen = DisabledScreenFactory()
        payload = {
            'screen_id': screen.id,
            'number': self.faker.random_int(1, 200),
            'row': self.faker.random_int(1, 200),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Screen not found'}
