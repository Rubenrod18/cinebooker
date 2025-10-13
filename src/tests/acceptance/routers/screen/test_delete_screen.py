from app.models import Screen
from tests.acceptance.routers.screen._base_screens_test import _TestBaseScreenEndpoints
from tests.common.factories.screen_factory import DisabledScreenFactory, EnabledScreenFactory


class TestDeleteScreenRouter(_TestBaseScreenEndpoints):
    def test_not_found(self):
        response = self.client.delete(url=f'{self.base_path}/99', json={}, exp_code=404)

        assert response.json() == {'detail': 'Screen not found'}

    def test_delete_disabled_screen(self):
        screen = DisabledScreenFactory()

        response = self.client.delete(url=f'{self.base_path}/{screen.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Screen not found'}

    def test_delete_enabled_screen(self):
        screen = EnabledScreenFactory()

        self.client.delete(url=f'{self.base_path}/{screen.id}', json={}, exp_code=204)

        with self.app.container.session() as session:
            found_screen = session.query(Screen).first()
            assert found_screen
            assert found_screen.id == screen.id
            assert found_screen.is_inactived
