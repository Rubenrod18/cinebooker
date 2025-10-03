from app.models import Screen
from tests.acceptance.routers.screen._base_screens_test import _TestBaseScreenEndpoints
from tests.common.factories.screen_factory import DisabledScreenFactory, EnabledScreenFactory


class TestUpdateScreenRouter(_TestBaseScreenEndpoints):
    def test_not_found(self):
        response = self.client.patch(url=f'{self.base_path}/99', json={}, exp_code=404)
        json_response = response.json()

        assert json_response
        assert json_response == {'detail': 'Screen not found'}

    def test_no_update_fields(self):
        screen = EnabledScreenFactory()
        current_screen = {'name': screen.name, 'capacity': screen.capacity}

        response = self.client.patch(
            url=f'{self.base_path}/{screen.id}',
            json={},
        )
        json_response = response.json()

        assert json_response
        assert json_response['name'] == current_screen['name']
        assert json_response['capacity'] == current_screen['capacity']

        with self.app.container.session() as session:
            found_screen = session.query(Screen).first()
            assert found_screen
            assert found_screen.name == current_screen['name']
            assert found_screen.capacity == current_screen['capacity']

    def test_update_name_screen(self):
        screen = EnabledScreenFactory()
        payload = {'name': self.faker.name()}

        response = self.client.patch(
            url=f'{self.base_path}/{screen.id}',
            json=payload,
        )
        json_response = response.json()

        assert json_response
        assert json_response['name'] == payload['name']
        assert json_response['capacity'] == screen.capacity

        with self.app.container.session() as session:
            screen = session.query(Screen).first()
            assert screen
            assert screen.name == payload['name']

    def test_update_capacity_screen(self):
        screen = EnabledScreenFactory()
        payload = {'capacity': self.faker.random_int(1, 200)}

        response = self.client.patch(
            url=f'{self.base_path}/{screen.id}',
            json=payload,
        )
        json_response = response.json()

        assert json_response
        assert json_response['name'] == screen.name
        assert json_response['capacity'] == payload['capacity']

        with self.app.container.session() as session:
            found_screen = session.query(Screen).first()
            assert found_screen
            assert found_screen.capacity == payload['capacity']

    def test_update_invalid_capacity_screen(self):
        screen = EnabledScreenFactory()
        payload = {'capacity': 0}

        response = self.client.patch(
            url=f'{self.base_path}/{screen.id}',
            json=payload,
            exp_code=422,
        )

        assert response.json() == {
            'detail': [
                {
                    'type': 'greater_than_equal',
                    'loc': ['body', 'capacity'],
                    'msg': 'Input should be greater than or equal to 1',
                    'input': 0,
                    'ctx': {'ge': 1},
                }
            ]
        }

    def test_update_disabled_screen(self):
        screen = DisabledScreenFactory()

        response = self.client.patch(url=f'{self.base_path}/{screen.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Screen not found'}
