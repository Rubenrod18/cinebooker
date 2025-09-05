from sqlalchemy import create_engine, text

from app.cli.base_cli import BaseCli


class CreateDatabaseCli(BaseCli):
    def __init__(self, db_uri: str):
        self.db_uri = db_uri
        self.engine = create_engine(self.db_uri)

    def create_database_if_not_exists(self, dbname: str) -> bool:
        base_uri, _ = self.db_uri.rsplit('/', 1)

        engine = create_engine(f'{base_uri}/postgres', isolation_level='AUTOCOMMIT')

        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}';")).fetchone()
            if not result:
                conn.execute(text(f'CREATE DATABASE "{dbname}";'))

            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}';")).fetchone()

            if not result:
                raise RuntimeError(f"Failed to create the database: '{dbname}'.")

            return True

    def run_command(self, *args, **kwargs):
        dbname = self.db_uri.rsplit('/', 1)[1]

        self.create_database_if_not_exists(dbname)

        print(f'Database "{dbname}" exists or was created successfully!')  # noqa
