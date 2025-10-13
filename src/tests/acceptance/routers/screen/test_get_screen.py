from tests.acceptance.routers.screen._base_screens_test import _TestBaseScreenEndpoints
from tests.common.factories.screen_factory import DisabledScreenFactory, EnabledScreenFactory


class TestGetScreenRouter(_TestBaseScreenEndpoints):
    def test_not_found(self):
        response = self.client.get(url=f'{self.base_path}/99', json={}, exp_code=404)

        assert response.json() == {'detail': 'Screen not found'}

    def test_find_by_id_disabled_screen(self):
        screen = DisabledScreenFactory()

        response = self.client.get(url=f'{self.base_path}/{screen.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Screen not found'}

    def test_find_by_id_enabled_screen(self):
        screen = EnabledScreenFactory()

        response = self.client.get(url=f'{self.base_path}/{screen.id}', json={})
        json_response = response.json()

        assert json_response
        assert json_response['name'] == screen.name
        assert json_response['capacity'] == screen.capacity
