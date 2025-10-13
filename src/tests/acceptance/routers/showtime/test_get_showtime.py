import uuid

from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.showtime._base_showtime_test import _TestBaseShowtimeEndpoints
from tests.common.factories.showtime_factory import ShowtimeFactory


class TestGetShowtimeRouter(_TestBaseShowtimeEndpoints):
    def test_not_found(self):
        response = self.client.get(url=f'{self.base_path}/{uuid.uuid4()}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Showtime not found'}

    def test_find_by_id_showtime(self):
        showtime = ShowtimeFactory()

        response = self.client.get(url=f'{self.base_path}/{showtime.id}', json={})
        json_response = response.json()

        assert json_response
        assert json_response['movie_id'] == showtime.movie_id
        assert json_response['screen_id'] == showtime.screen_id
        assert json_response['start_time'] == showtime.start_time.strftime(DEFAULT_DATETIME_FORMAT)
        assert json_response['base_price'] == str(showtime.base_price)
        assert json_response['vat_rate'] == str(showtime.vat_rate)
        assert json_response['price_with_vat'] == str(showtime.price_with_vat)
