import random
from datetime import timedelta

import factory

from app.models import Movie
from app.models.movie import MovieGenre

from .base_factory import BaseFactory


class MovieFactory(BaseFactory):
    class Meta:
        model = Movie

    title = factory.Sequence(lambda n: f'Movie title {n}')
    description = factory.Sequence(lambda n: f'Movie description {n}')
    duration = factory.Faker('pyint', min_value=60, max_value=240)
    release_date = factory.Faker('date_between', start_date='-30y', end_date='-5y')
    genre = factory.Iterator(MovieGenre.to_list())
    director = factory.Faker('name')
    language = factory.Faker('language_name')
    created_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    updated_at = factory.Faker('date_time_between', start_date='-1y', end_date='now')

    @factory.lazy_attribute
    def inactive_at(self):
        return random.choice([self.created_at + timedelta(days=2), None])


class EnabledMovieFactory(MovieFactory):
    inactive_at = None


class DisabledMovieFactory(MovieFactory):
    @factory.lazy_attribute
    def inactive_at(self):
        return self.created_at + timedelta(days=2)


class ActionMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.ACTION.value


class ComedyMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.COMEDY.value


class DramaMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.DRAMA.value


class HorrorMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.HORROR.value


class RomanceMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.ROMANCE.value


class ScienceFictionMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.SCIENCE_FICTION.value


class ThrillerMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.THRILLER.value


class AnimationMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.ANIMATION.value


class DocumentaryMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.DOCUMENTARY.value


class FantasyMovieFactory(EnabledMovieFactory):
    genre = MovieGenre.FANTASY.value
