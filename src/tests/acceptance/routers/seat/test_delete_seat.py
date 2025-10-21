from app.models import Seat
from tests.acceptance.routers.seat._base_seats_test import _TestBaseSeatEndpoints
from tests.common.factories.seat_factory import DisabledSeatFactory, EnabledSeatFactory


class TestDeleteSeatRouter(_TestBaseSeatEndpoints):
    def test_not_found(self):
        response = self.client.delete(url=f'{self.base_path}/99', json={}, exp_code=404)

        assert response.json() == {'detail': 'Seat not found'}

    def test_delete_disabled_seat(self):
        seat = DisabledSeatFactory()

        response = self.client.delete(url=f'{self.base_path}/{seat.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Seat not found'}

    def test_delete_enabled_seat(self):
        seat = EnabledSeatFactory()

        self.client.delete(url=f'{self.base_path}/{seat.id}', json={}, exp_code=204)

        with self.app.container.session() as session:
            found_seat = session.query(Seat).first()
            assert found_seat
            assert found_seat.id == seat.id
            assert found_seat.is_inactived
