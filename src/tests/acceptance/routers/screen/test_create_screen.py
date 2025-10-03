from app.models import Screen
from tests.acceptance.routers.screen._base_screens_test import _TestBaseScreenEndpoints


class TestCreateScreenEndpoint(_TestBaseScreenEndpoints):
    def test_create_screen(self):
        payload = {
            'name': self.faker.first_name(),
            'capacity': self.faker.random_int(1, 200),
        }

        response = self.client.post(url=self.base_path, json=payload)
        json_response = response.json()

        assert json_response
        assert json_response['name'] == payload['name']
        assert json_response['capacity'] == payload['capacity']

        with self.app.container.session() as session:
            screen = session.query(Screen).first()
            assert screen
            assert screen.name == payload['name']
            assert screen.capacity == payload['capacity']

    def test_invalid_capacity(self):
        payload = {
            'name': self.faker.first_name(),
            'capacity': 0,
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'ctx': {'ge': 1},
                    'input': 0,
                    'loc': ['body', 'capacity'],
                    'msg': 'Input should be greater than or equal to 1',
                    'type': 'greater_than_equal',
                }
            ]
        }
