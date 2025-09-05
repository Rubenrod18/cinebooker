import logging
import os
import typing as t
from collections.abc import Callable
from contextlib import AbstractContextManager, contextmanager

from sqlalchemy import create_engine, orm
from sqlalchemy.orm import Session

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
_S = t.TypeVar('_S', bound='Session')


class SQLDatabase:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, echo=True)
        self._sessionmaker = orm.sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine, expire_on_commit=False
        )
        self._session_factory = orm.scoped_session(self._sessionmaker)

    @property
    def sessionmaker(self) -> t.Generic[_S]:
        return self._sessionmaker

    @property
    def session_factory(self) -> t.Generic[_S]:
        return self._session_factory

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            logger.exception('Session rollback because of exception')
            session.rollback()
            raise
        finally:
            session.close()


def get_session() -> Session:
    sql_db = SQLDatabase(db_url=os.getenv('SQLALCHEMY_DATABASE_URI'))
    return sql_db.session_factory
