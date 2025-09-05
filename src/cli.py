"""CLI module for managing custom commands of the application."""

import typer

from app.cli import CreateDatabaseCli, SeederCli
from database import settings

app = typer.Typer()


@app.command(name='create_db', help='Create database.')
def create_database() -> None:
    """Command line script for creating the database."""
    cli = CreateDatabaseCli(db_uri=settings.DATABASE_URL)
    cli.run_command()


@app.command(name='seed', help='Fill database with fake data.')
def seeds() -> None:
    """Command line script for filling database with fake data."""
    cli = SeederCli()
    cli.run_command()


if __name__ == '__main__':
    app()
