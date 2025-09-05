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


class ActionMovieFactory(MovieFactory):
    genre = MovieGenre.ACTION.value


class ComedyMovieFactory(MovieFactory):
    genre = MovieGenre.COMEDY.value


class DramaMovieFactory(MovieFactory):
    genre = MovieGenre.DRAMA.value


class HorrorMovieFactory(MovieFactory):
    genre = MovieGenre.HORROR.value


class RomanceMovieFactory(MovieFactory):
    genre = MovieGenre.ROMANCE.value


class ScienceFictionMovieFactory(MovieFactory):
    genre = MovieGenre.SCIENCE_FICTION.value


class ThrillerMovieFactory(MovieFactory):
    genre = MovieGenre.THRILLER.value


class AnimationMovieFactory(MovieFactory):
    genre = MovieGenre.ANIMATION.value


class DocumentaryMovieFactory(MovieFactory):
    genre = MovieGenre.DOCUMENTARY.value


class FantasyMovieFactory(MovieFactory):
    genre = MovieGenre.FANTASY.value
