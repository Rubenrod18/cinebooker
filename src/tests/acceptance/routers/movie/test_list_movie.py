from datetime import datetime, timedelta

import pytest

from app.utils.constants import DEFAULT_DATE_FORMAT, DEFAULT_DATETIME_FORMAT
from tests.acceptance.routers.movie._base_movies_test import _TestBaseMovieEndpoints
from tests.common.factories.movie_factory import DisabledMovieFactory, EnabledMovieFactory


class TestListMovieRouter(_TestBaseMovieEndpoints):
    def test_list_movies(self):
        current_dt = datetime.now()
        movie = EnabledMovieFactory(created_at=current_dt - timedelta(days=1))
        movie_2 = EnabledMovieFactory(created_at=current_dt)
        DisabledMovieFactory(created_at=current_dt)
        movies = [movie, movie_2]

        response = self.client.get(url=self.base_path)
        json_response = response.json()

        assert json_response
        assert len(json_response) == len(movies)

        for i, movie in enumerate(json_response):
            assert movie['title'] == movies[i].title
            assert movie['description'] == movies[i].description
            assert movie['duration'] == movies[i].duration
            assert movie['release_date'] == movies[i].release_date.strftime(DEFAULT_DATE_FORMAT)
            assert movie['genre'] == movies[i].genre
            assert movie['director'] == movies[i].director
            assert movie['language'] == movies[i].language
            assert movie['showtimes'] == []
            assert movie['created_at'] == movies[i].created_at.strftime(DEFAULT_DATETIME_FORMAT)
            assert movie['updated_at'] == movies[i].updated_at.strftime(DEFAULT_DATETIME_FORMAT)

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_movies',
        [
            (1, 3, 3),
            (2, 3, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_movies_found_filter_by_page_number(self, page_number, items_per_page, total_expected_movies):
        [EnabledMovieFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_movies

    @pytest.mark.parametrize(
        'page_number, items_per_page, total_expected_movies',
        [
            (1, 1, 1),
            (4, 1, 0),
        ],
        ids=['page_1', 'page_2'],
    )
    def test_get_movies_found_filter_by_items_per_page(self, page_number, items_per_page, total_expected_movies):
        [EnabledMovieFactory() for _ in range(3)]
        query_params = f'page_number={page_number}&items_per_page={items_per_page}'

        response = self.client.get(url=f'{self.base_path}?{query_params}')
        json_response = response.json()

        assert len(json_response) == total_expected_movies
