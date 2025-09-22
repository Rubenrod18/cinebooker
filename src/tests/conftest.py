import logging
import os
import uuid

import httpx
import pytest
import sqlalchemy as sa
from dotenv import find_dotenv, load_dotenv
from faker import Faker
from faker.providers import date_time
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from app import create_app
from app.cli import CreateDatabaseCli
from app.models.core import IntegerPKMixin, UUIDPKMixin
from tests.common.factories.base_factory import BaseFactory

logger = logging.getLogger(__name__)

fake = Faker()
fake.add_provider(date_time)


class _CustomTestClient(TestClient):
    @staticmethod
    def _before_request(*args, **kwargs):
        logger.info(f'args: {args}')
        logger.info(f'kwargs: {kwargs}')

    @staticmethod
    def _log_request_data(response: httpx.Response):
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type and response.content:
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
        else:
            response_data = response.text  # or response.content for raw bytes
        logger.info(f'response data: {response_data}')

    def _after_request(self, response: httpx.Response):
        logger.info(f'response status code: {response.status_code}')
        logger.info(f'response mime type: {response.headers.get("content-type", "")}')
        self._log_request_data(response)

    def _make_request(self, expected_status_code: int, *args, **kwargs):
        logger.info('< === START REQUEST === >')
        self._before_request(*args, **kwargs)
        response = self.request(*args, **kwargs)
        self._after_request(response)
        logger.info('< === END REQUEST === >')

        assert response.status_code == expected_status_code, response.text
        return response

    def get(self, *args, **kwargs):
        exp_code = kwargs.pop('exp_code', 200)
        return self._make_request(exp_code, *args, method='GET', **kwargs)

    def post(self, *args, **kwargs):
        exp_code = kwargs.pop('exp_code', 201)
        return self._make_request(exp_code, *args, method='POST', **kwargs)

    def put(self, *args, **kwargs):
        exp_code = kwargs.pop('exp_code', 200)
        return self._make_request(exp_code, *args, method='PUT', **kwargs)

    def delete(self, *args, **kwargs):
        exp_code = kwargs.pop('exp_code', 200)
        return self._make_request(exp_code, *args, method='DELETE', **kwargs)


def pytest_configure():
    """Load .env.test before running tests"""
    load_dotenv(find_dotenv('.env.test'), override=True)


@pytest.fixture(scope='function', autouse=True)
def setup_database():
    def create_new_sqlalchemy_session(session: sa.orm.Session) -> tuple[str, sa.Engine, str]:
        test_db_uri = f'{os.environ["SQLALCHEMY_DATABASE_URI"]}_{uuid.uuid4().hex}'
        test_engine = sa.create_engine(test_db_uri)
        session.configure(bind=test_engine)
        original_db_uri = os.environ['SQLALCHEMY_DATABASE_URI']
        return original_db_uri, test_engine, test_db_uri

    def create_db(engine: sa.Engine, test_db_uri: str):
        seeder_cli = CreateDatabaseCli(db_uri=test_db_uri)
        seeder_cli.run_command()

        with engine.begin() as conn:
            IntegerPKMixin.metadata.create_all(conn)
            UUIDPKMixin.metadata.create_all(conn)

    def drop_db(engine: sa.Engine, session: sa.orm.Session):
        db_name_to_drop = engine.url.database
        neutral_engine_url = engine.url.set(database='postgres')
        neutral_engine = sa.create_engine(neutral_engine_url, echo=True)

        try:
            with neutral_engine.connect() as conn:
                conn.execution_options(isolation_level='AUTOCOMMIT')
                conn.execute(
                    sa.text(f"""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = '{db_name_to_drop}';
                """)
                )
                conn.execute(sa.text(f'DROP DATABASE IF EXISTS "{db_name_to_drop}"'))
                print(f"Database '{db_name_to_drop}' dropped successfully.")  # noqa
        finally:
            session.remove()
            neutral_engine.dispose()

    sqlalchemy_session = BaseFactory.get_db_session()
    db_uri, sa_engine, test_db_uri = create_new_sqlalchemy_session(sqlalchemy_session)
    create_db(sa_engine, test_db_uri)
    yield test_db_uri
    drop_db(sa_engine, sqlalchemy_session)
    os.environ['SQLALCHEMY_DATABASE_URI'] = db_uri


@pytest.fixture
def app(setup_database):
    app = create_app()
    app.container.config.from_dict({'SQLALCHEMY_DATABASE_URI': setup_database})
    return app


@pytest.fixture
def client(app):
    return _CustomTestClient(app)


@pytest.fixture
def runner():
    """Provide a Typer CLI runner."""
    return CliRunner()


@pytest.fixture(scope='session')
def faker():
    return fake
