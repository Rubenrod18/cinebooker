import random

from app.models import Movie
from app.models.movie import MovieGenre
from app.utils.constants import DEFAULT_DATE_FORMAT
from tests.acceptance.routers.movie._base_movies_test import _TestBaseMovieEndpoints


class TestCreateMovieEndpoint(_TestBaseMovieEndpoints):
    def test_create_movie(self):
        release_date = self.faker.date_between(start_date='-10y', end_date='today')
        payload = {
            'title': self.faker.sentence(nb_words=3).replace('.', ''),
            'description': self.faker.paragraph(nb_sentences=3),
            'duration': random.randint(80, 180),  # minutes
            'release_date': release_date.strftime(DEFAULT_DATE_FORMAT),
            'genre': random.choice(list(MovieGenre)).value,
            'director': self.faker.name(),
            'language': random.choice(['English', 'Spanish', 'French', 'German', 'Italian']),
        }

        response = self.client.post(url=self.base_path, json=payload)
        json_response = response.json()

        assert json_response
        assert json_response['title'] == payload['title']
        assert json_response['description'] == payload['description']
        assert json_response['duration'] == payload['duration']
        assert json_response['release_date'] == payload['release_date']
        assert json_response['genre'] == payload['genre']
        assert json_response['director'] == payload['director']
        assert json_response['language'] == payload['language']

        with self.app.container.session() as session:
            movie = session.query(Movie).first()
            assert movie
            assert movie.title == payload['title']
            assert movie.description == payload['description']
            assert movie.duration == payload['duration']
            assert movie.release_date == release_date
            assert movie.genre == payload['genre']
            assert movie.director == payload['director']
            assert movie.language == payload['language']
            assert movie.is_actived
