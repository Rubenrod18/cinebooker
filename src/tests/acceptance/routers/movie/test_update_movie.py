import random

import pytest

from app.models import Movie
from app.models.movie import MovieGenre
from app.utils.constants import DEFAULT_DATE_FORMAT
from tests.acceptance.routers.movie._base_movies_test import _TestBaseMovieEndpoints
from tests.common.factories.movie_factory import DisabledMovieFactory, EnabledMovieFactory


class TestUpdateMovieRouter(_TestBaseMovieEndpoints):
    def test_not_found(self):
        response = self.client.patch(url=f'{self.base_path}/99', json={}, exp_code=404)
        json_response = response.json()

        assert json_response
        assert json_response == {'detail': 'Movie not found'}

    def test_no_update_fields(self):
        movie = EnabledMovieFactory()
        current_movie = {
            'title': movie.title,
            'description': movie.description,
            'duration': movie.duration,
            'release_date': movie.release_date,
            'genre': movie.genre,
            'director': movie.director,
            'language': movie.language,
        }

        response = self.client.patch(
            url=f'{self.base_path}/{movie.id}',
            json={},
        )
        json_response = response.json()

        assert json_response
        assert json_response['title'] == current_movie['title']
        assert json_response['description'] == current_movie['description']
        assert json_response['duration'] == current_movie['duration']
        assert json_response['release_date'] == current_movie['release_date'].strftime(DEFAULT_DATE_FORMAT)
        assert json_response['genre'] == current_movie['genre']
        assert json_response['director'] == current_movie['director']
        assert json_response['language'] == current_movie['language']

        with self.app.container.session() as session:
            found_movie = session.query(Movie).first()
            assert found_movie
            assert found_movie.title == current_movie['title']
            assert found_movie.description == current_movie['description']
            assert found_movie.duration == current_movie['duration']
            assert found_movie.release_date == current_movie['release_date']
            assert found_movie.genre == current_movie['genre']
            assert found_movie.director == current_movie['director']
            assert found_movie.language == current_movie['language']

    @pytest.mark.parametrize(
        'pre_payload, field',
        (
            (lambda x: {'title': x.sentence(nb_words=3).replace('.', '')}, 'title'),
            (lambda x: {'description': x.paragraph(nb_sentences=3)}, 'description'),
            (lambda x: {'duration': random.randint(80, 180)}, 'duration'),
            (
                lambda x: {
                    'release_date': x.date_between(start_date='-10y', end_date='today').strftime(DEFAULT_DATE_FORMAT)
                },
                'release_date',
            ),
            (lambda x: {'genre': random.choice(list(MovieGenre)).value}, 'genre'),
            (lambda x: {'director': x.name()}, 'director'),
            (lambda x: {'language': random.choice(['English', 'Spanish', 'French', 'German', 'Italian'])}, 'language'),
        ),
        ids=['title', 'description', 'duration', 'release_date', 'genre', 'director', 'language'],
    )
    def test_update_field(self, pre_payload, field):
        movie = EnabledMovieFactory()
        payload = pre_payload(self.faker)

        response = self.client.patch(
            url=f'{self.base_path}/{movie.id}',
            json=payload,
        )
        json_response = response.json()

        assert json_response
        assert json_response[field] == payload[field]

        with self.app.container.session() as session:
            movie = session.query(Movie).first()
            assert movie
            if field == 'release_date':
                assert getattr(movie, field).strftime(DEFAULT_DATE_FORMAT) == payload[field]
            else:
                assert getattr(movie, field) == payload[field]

    def test_update_disabled_movie(self):
        movie = DisabledMovieFactory()

        response = self.client.patch(url=f'{self.base_path}/{movie.id}', json={}, exp_code=404)

        assert response.json() == {'detail': 'Movie not found'}
