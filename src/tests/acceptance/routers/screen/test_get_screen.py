from app.utils.constants import DEFAULT_DATETIME_FORMAT
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

        assert response.json() == {
            'capacity': screen.capacity,
            'created_at': screen.created_at.strftime(DEFAULT_DATETIME_FORMAT),
            'id': screen.id,
            'inactive_at': None,
            'name': screen.name,
            'updated_at': screen.updated_at.strftime(DEFAULT_DATETIME_FORMAT),
        }
