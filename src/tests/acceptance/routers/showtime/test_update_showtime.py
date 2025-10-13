import uuid

from app.models import Showtime
from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.showtime._base_showtime_test import _TestBaseShowtimeEndpoints
from tests.common.factories.showtime_factory import ShowtimeFactory


class TestUpdateShowtimeRouter(_TestBaseShowtimeEndpoints):
    def test_not_found(self):
        response = self.client.patch(url=f'{self.base_path}/{uuid.uuid4()}', json={}, exp_code=404)
        json_response = response.json()

        assert json_response
        assert json_response == {'detail': 'Showtime not found'}

    def test_no_update_fields(self):
        showtime = ShowtimeFactory()
        current_showtime = {
            'movie_id': showtime.movie_id,
            'screen_id': showtime.screen_id,
            'start_time': showtime.start_time,
            'base_price': showtime.base_price,
            'vat_rate': showtime.vat_rate,
            'price_with_vat': showtime.price_with_vat,
        }

        response = self.client.patch(
            url=f'{self.base_path}/{showtime.id}',
            json={},
        )
        json_response = response.json()

        assert json_response
        assert json_response['movie_id'] == current_showtime['movie_id']
        assert json_response['screen_id'] == current_showtime['screen_id']
        assert json_response['start_time'] == current_showtime['start_time'].strftime(DEFAULT_DATETIME_FORMAT)
        assert json_response['base_price'] == str(current_showtime['base_price'])
        assert json_response['vat_rate'] == str(current_showtime['vat_rate'])
        assert json_response['price_with_vat'] == str(current_showtime['price_with_vat'])

        with self.app.container.session() as session:
            found_showtime = session.query(Showtime).first()
            assert found_showtime
            assert found_showtime.movie_id == current_showtime['movie_id']
            assert found_showtime.screen_id == current_showtime['screen_id']
            assert found_showtime.start_time == current_showtime['start_time']
            assert found_showtime.base_price == current_showtime['base_price']
            assert found_showtime.vat_rate == current_showtime['vat_rate']
            assert found_showtime.price_with_vat == current_showtime['price_with_vat']
