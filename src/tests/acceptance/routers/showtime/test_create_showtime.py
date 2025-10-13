from app.models import Showtime
from app.utils.constants import DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.showtime._base_showtime_test import _TestBaseShowtimeEndpoints
from tests.common.factories.movie_factory import EnabledMovieFactory
from tests.common.factories.screen_factory import EnabledScreenFactory
from tests.common.factories.showtime_factory import ShowtimeFactory


class TestCreateShowtimeEndpoint(_TestBaseShowtimeEndpoints):
    def test_create_showtime(self):
        movie = EnabledMovieFactory()
        screen = EnabledScreenFactory()
        showtime = ShowtimeFactory.build_dict(only={'start_time', 'base_price', 'vat_rate', 'price_with_vat'})
        payload = {
            'movie_id': movie.id,
            'screen_id': screen.id,
            'start_time': showtime['start_time'].strftime(DEFAULT_DATETIME_FORMAT),
            'base_price': str(showtime['base_price']),
            'vat_rate': str(showtime['vat_rate']),
            'price_with_vat': str(showtime['price_with_vat']),
        }

        response = self.client.post(url=self.base_path, json=payload)
        json_response = response.json()

        assert json_response
        assert json_response['movie_id'] == payload['movie_id']
        assert json_response['start_time'] == payload['start_time']
        assert json_response['base_price'] == payload['base_price']
        assert json_response['vat_rate'] == payload['vat_rate']
        assert json_response['price_with_vat'] == payload['price_with_vat']

        with self.app.container.session() as session:
            showtime = session.query(Showtime).first()
            assert showtime
            assert showtime.movie_id == payload['movie_id']
            assert showtime.screen_id == payload['screen_id']
            assert showtime.start_time.strftime(DEFAULT_DATETIME_FORMAT) == payload['start_time']
            assert str(showtime.base_price) == payload['base_price']
            assert str(showtime.vat_rate) == payload['vat_rate']
            assert str(showtime.price_with_vat) == payload['price_with_vat']

    def test_invalid_start_datetime(self):
        movie = EnabledMovieFactory()
        screen = EnabledScreenFactory()
        showtime = ShowtimeFactory.build_dict(only={'base_price', 'vat_rate', 'price_with_vat'})
        payload = {
            'movie_id': movie.id,
            'screen_id': screen.id,
            'start_time': self.faker.date_time_between(start_date='-1y', end_date='now').strftime(
                DEFAULT_DATETIME_FORMAT
            ),
            'base_price': str(showtime['base_price']),
            'vat_rate': str(showtime['vat_rate']),
            'price_with_vat': str(showtime['price_with_vat']),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'input': payload['start_time'],
                    'loc': [
                        'body',
                        'start_time',
                    ],
                    'msg': 'Input should be in the future',
                    'type': 'datetime_future',
                },
            ],
        }

    def test_invalid_price_fields(self):
        movie = EnabledMovieFactory()
        screen = EnabledScreenFactory()
        showtime = ShowtimeFactory.build_dict(only={'start_time', 'base_price', 'vat_rate', 'price_with_vat'})
        payload = {
            'movie_id': movie.id,
            'screen_id': screen.id,
            'start_time': showtime['start_time'].strftime(DEFAULT_DATETIME_FORMAT),
            'base_price': str(0),
            'vat_rate': str(-1),
            'price_with_vat': str(0),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=422)

        assert response.json() == {
            'detail': [
                {
                    'ctx': {
                        'ge': 1,
                    },
                    'input': '0',
                    'loc': [
                        'body',
                        'base_price',
                    ],
                    'msg': 'Input should be greater than or equal to 1',
                    'type': 'greater_than_equal',
                },
                {
                    'ctx': {
                        'gt': 0,
                    },
                    'input': '-1',
                    'loc': [
                        'body',
                        'vat_rate',
                    ],
                    'msg': 'Input should be greater than 0',
                    'type': 'greater_than',
                },
                {
                    'ctx': {
                        'ge': 1,
                    },
                    'input': '0',
                    'loc': [
                        'body',
                        'price_with_vat',
                    ],
                    'msg': 'Input should be greater than or equal to 1',
                    'type': 'greater_than_equal',
                },
            ],
        }

    def test_movie_not_found(self):
        screen = EnabledScreenFactory()
        showtime = ShowtimeFactory.build_dict(only={'base_price', 'vat_rate', 'price_with_vat'})
        payload = {
            'movie_id': 99,
            'screen_id': screen.id,
            'start_time': self.faker.date_time_between(start_date='-1y', end_date='now').strftime(
                DEFAULT_DATETIME_FORMAT
            ),
            'base_price': str(showtime['base_price']),
            'vat_rate': str(showtime['vat_rate']),
            'price_with_vat': str(showtime['price_with_vat']),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Movie not found'}

    def test_screen_not_found(self):
        movie = EnabledMovieFactory()
        showtime = ShowtimeFactory.build_dict(only={'base_price', 'vat_rate', 'price_with_vat'})
        payload = {
            'movie_id': movie.id,
            'screen_id': 99,
            'start_time': self.faker.date_time_between(start_date='-1y', end_date='now').strftime(
                DEFAULT_DATETIME_FORMAT
            ),
            'base_price': str(showtime['base_price']),
            'vat_rate': str(showtime['vat_rate']),
            'price_with_vat': str(showtime['price_with_vat']),
        }

        response = self.client.post(url=self.base_path, json=payload, exp_code=404)

        assert response.json() == {'detail': 'Screen not found'}
