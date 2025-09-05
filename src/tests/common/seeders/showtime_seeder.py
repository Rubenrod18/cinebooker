from datetime import datetime, timedelta, UTC

from app.models import Movie, Screen

from ..factories.showtime_factory import ShowtimeFactory
from . import seed_actions
from .core import FactorySeeder


def ceil_to_interval(dt: datetime, interval_min: int = 15) -> datetime:
    """Round dt *up* to the next `interval_min` minute boundary.

    If dt is already exactly on a boundary (and has no seconds/microseconds),
    it is returned unchanged. The returned datetime preserves tzinfo of dt.

    """
    truncated = dt.replace(second=0, microsecond=0)

    # Total minutes since midnight
    total_min = truncated.hour * 60 + truncated.minute
    remainder = total_min % interval_min

    if remainder == 0 and dt.second == 0 and dt.microsecond == 0:
        return truncated

    # Minutes to add to reach next boundary
    minutes_to_add = (interval_min - remainder) % interval_min
    if minutes_to_add == 0:
        minutes_to_add = interval_min

    return truncated + timedelta(minutes=minutes_to_add)


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='ShowtimeSeeder', priority=3, factory=ShowtimeFactory)
        self._showtimes_movie_per_day = 6

    @seed_actions
    def seed(self, *args, **kwargs) -> None:
        session = self.factory.get_db_session()
        movies = session.query(Movie).filter_by().all()
        screens = session.query(Screen).filter(Screen.inactive_at.is_(None)).all()
        ShowtimeFactory._meta.sqlalchemy_session = session
        showtime = None

        for screen in screens:
            for movie in movies:
                current_dt = datetime.now(UTC)
                for _ in range(self._showtimes_movie_per_day):
                    start_time = ceil_to_interval(showtime.end_time if showtime else current_dt, interval_min=15)

                    showtime = ShowtimeFactory.create(movie=movie, screen=screen, start_time=start_time)
