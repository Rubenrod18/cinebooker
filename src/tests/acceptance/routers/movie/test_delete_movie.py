from app.models import Movie
from tests.acceptance.routers.movie._base_movies_test import _TestBaseMovieEndpoints
from tests.common.factories.movie_factory import DisabledMovieFactory, EnabledMovieFactory


class TestDeleteMovieRouter(_TestBaseMovieEndpoints):
    def test_not_found(self):
        response = self.client.delete(url=f'{self.base_path}/99', json={}, exp_code=404)
        json_response = response.json()

        assert json_response
        assert json_response == {'detail': 'Movie not found'}

    def test_delete_disabled_movie(self):
        movie = DisabledMovieFactory()

        response = self.client.delete(url=f'{self.base_path}/{movie.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Movie not found'}

    def test_delete_enabled_movie(self):
        movie = EnabledMovieFactory()

        self.client.delete(url=f'{self.base_path}/{movie.id}', json={}, exp_code=204)

        with self.app.container.session() as session:
            found_movie = session.query(Movie).first()
            assert found_movie
            assert found_movie.id == movie.id
            assert found_movie.is_inactived
