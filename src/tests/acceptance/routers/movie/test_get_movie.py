from app.utils.constants import DEFAULT_DATE_FORMAT
from tests.acceptance.routers.movie._base_movies_test import _TestBaseMovieEndpoints
from tests.common.factories.movie_factory import DisabledMovieFactory, EnabledMovieFactory


class TestGetMovieRouter(_TestBaseMovieEndpoints):
    def test_not_found(self):
        response = self.client.get(url=f'{self.base_path}/99', json={}, exp_code=404)
        json_response = response.json()

        assert json_response
        assert json_response == {'detail': 'Movie not found'}

    def test_find_by_id_disabled_movie(self):
        movie = DisabledMovieFactory()

        response = self.client.get(url=f'{self.base_path}/{movie.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Movie not found'}

    def test_find_by_id_enabled_movie(self):
        movie = EnabledMovieFactory()

        response = self.client.get(url=f'{self.base_path}/{movie.id}', json={})
        json_response = response.json()

        assert json_response
        assert json_response['title'] == movie.title
        assert json_response['description'] == movie.description
        assert json_response['duration'] == movie.duration
        assert json_response['release_date'] == movie.release_date.strftime(DEFAULT_DATE_FORMAT)
        assert json_response['genre'] == movie.genre
        assert json_response['director'] == movie.director
        assert json_response['language'] == movie.language
        assert json_response['showtimes'] == []
