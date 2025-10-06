"""Module for managing dependency injections."""

import os

from dependency_injector import containers, providers
from dotenv import load_dotenv

from app.repositories.auth_user_repository import AuthUserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.movie_repository import MovieRepository
from app.repositories.screen_repository import ScreenRepository
from app.services.auth_user_service import AuthUserService
from app.services.customer_service import CustomerService
from app.services.movie_service import MovieService
from app.services.screen_service import ScreenService
from config import get_settings
from database import SQLDatabase

settings = get_settings()
load_dotenv()


class ServiceDIContainer(containers.DeclarativeContainer):
    """Service Dependency Injection Container."""

    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(
        modules=[
            '.routers.base',
            '.routers.customer_router',
            '.routers.screen_router',
            '.schemas.screen_schemas',
            '.routers.movie_router',
            '.schemas.movie_schemas',
        ]
    )
    # OPTIMIZE: Load all env vars on this config
    config.from_dict({'SQLALCHEMY_DATABASE_URI': os.getenv('SQLALCHEMY_DATABASE_URI')})

    # Database
    sql_db = providers.Singleton(SQLDatabase, db_url=config.SQLALCHEMY_DATABASE_URI)
    session = providers.Resource(
        lambda db: db.sessionmaker(),
        db=sql_db,
    )

    # Repositories
    auth_user_repository = providers.Factory(AuthUserRepository, session=session)
    customer_repository = providers.Factory(CustomerRepository, session=session)
    movie_repository = providers.Factory(MovieRepository, session=session)
    screen_repository = providers.Factory(ScreenRepository, session=session)

    # Services
    auth_user_service = providers.Factory(AuthUserService, session=session, auth_user_repository=auth_user_repository)
    customer_service = providers.Factory(CustomerService, session=session, customer_repository=customer_repository)
    movie_service = providers.Factory(MovieService, session=session, movie_repository=movie_repository)
    screen_service = providers.Factory(ScreenService, session=session, screen_repository=screen_repository)
