"""Module for managing dependency injections."""

import os

from dependency_injector import containers, providers
from dotenv import load_dotenv

from app.providers.paypal_provider import PayPalProvider
from app.providers.stripe_provider import StripeProvider
from app.repositories.auth_user_repository import AuthUserRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.booking_seat_repository import BookingSeatRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.discount_repository import DiscountRepository
from app.repositories.movie_repository import MovieRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.screen_repository import ScreenRepository
from app.repositories.seat_repository import SeatRepository
from app.repositories.showtime_repository import ShowtimeRepository
from app.services.auth_user_service import AuthUserService
from app.services.booking_seat_service import BookingSeatService
from app.services.booking_service import BookingService
from app.services.customer_service import CustomerService
from app.services.discount_service import DiscountService
from app.services.movie_service import MovieService
from app.services.payment_service import PaymentService
from app.services.screen_service import ScreenService
from app.services.seat_service import SeatService
from app.services.showtime_service import ShowtimeService
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
            '.routers.booking_router',
            '.schemas.booking_schemas',
            '.routers.booking_seat_router',
            '.schemas.booking_seat_schemas',
            '.routers.customer_router',
            '.routers.screen_router',
            '.schemas.screen_schemas',
            '.routers.movie_router',
            '.schemas.movie_schemas',
            '.routers.discount_router',
            '.schemas.discount_schemas',
            '.schemas.payment_schemas',
            '.routers.paypal_router',
            '.schemas.paypal_schemas',
            '.routers.seat_router',
            '.schemas.seat_schemas',
            '.routers.showtime_router',
            '.schemas.showtime_schemas',
            '.routers.stripe_router',
            '.schemas.stripe_schemas',
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

    # Providers
    paypal_provider = providers.Singleton(
        PayPalProvider,
        client_id=settings.PAYPAL_CLIENT_ID,
        client_secret=settings.PAYPAL_CLIENT_SECRET,
        webhook_id=settings.PAYPAL_WEBHOOK_ID,
        sandbox=settings.PAYPAL_SANDBOX,
    )
    stripe_provider = providers.Singleton(StripeProvider, api_key=settings.STRIPE_API_KEY)

    # Repositories
    auth_user_repository = providers.Factory(AuthUserRepository, session=session)
    booking_repository = providers.Factory(BookingRepository, session=session)
    booking_seat_repository = providers.Factory(BookingSeatRepository, session=session)
    customer_repository = providers.Factory(CustomerRepository, session=session)
    discount_repository = providers.Factory(DiscountRepository, session=session)
    movie_repository = providers.Factory(MovieRepository, session=session)
    payment_repository = providers.Factory(PaymentRepository, session=session)
    screen_repository = providers.Factory(ScreenRepository, session=session)
    seat_repository = providers.Factory(SeatRepository, session=session)
    showtime_repository = providers.Factory(ShowtimeRepository, session=session)

    # Services
    auth_user_service = providers.Factory(AuthUserService, session=session, auth_user_repository=auth_user_repository)
    booking_service = providers.Factory(
        BookingService,
        session=session,
        booking_repository=booking_repository,
        paypal_provider=paypal_provider,
        stripe_provider=stripe_provider,
    )
    booking_seat_service = providers.Factory(
        BookingSeatService, session=session, booking_seat_repository=booking_seat_repository
    )
    customer_service = providers.Factory(CustomerService, session=session, customer_repository=customer_repository)
    discount_service = providers.Factory(DiscountService, session=session, discount_repository=discount_repository)
    movie_service = providers.Factory(MovieService, session=session, movie_repository=movie_repository)
    payment_service = providers.Factory(PaymentService, session=session, payment_repository=payment_repository)
    screen_service = providers.Factory(ScreenService, session=session, screen_repository=screen_repository)
    seat_service = providers.Factory(SeatService, session=session, screen_repository=seat_repository)
    showtime_service = providers.Factory(ShowtimeService, session=session, showtime_repository=showtime_repository)
