import os
from decimal import Decimal
from functools import lru_cache

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class BaseConfig(BaseSettings):
    APP_NAME: str = 'Cinebooker'
    DEBUG: bool = False

    # SQLAlchemy
    DATABASE_URL: str = os.getenv('SQLALCHEMY_DATABASE_URI')

    # Stripe
    STRIPE_API_KEY: str = os.getenv('STRIPE_API_KEY')
    STRIPE_WEBHOOK_SECRET: str = os.getenv('STRIPE_WEBHOOK_SECRET')

    # Paypal
    PAYPAL_CLIENT_ID: str = os.getenv('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET: str = os.getenv('PAYPAL_CLIENT_SECRET')
    PAYPAL_WEBHOOK_ID: str = os.getenv('PAYPAL_WEBHOOK_ID')
    PAYPAL_SANDBOX: bool = os.getenv('PAYPAL_SANDBOX')

    # FastAPI-Mail
    MAIL_USERNAME: str = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD')
    MAIL_FROM: str = os.getenv('MAIL_FROM')
    MAIL_PORT: int = os.getenv('MAIL_PORT')
    MAIL_SERVER: str = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME: str = os.getenv('MAIL_FROM_NAME')
    MAIL_STARTTLS: bool = os.getenv('MAIL_STARTTLS')
    MAIL_SSL_TLS: bool = os.getenv('MAIL_SSL_TLS')
    USE_CREDENTIALS: bool = os.getenv('USE_CREDENTIALS')
    VALIDATE_CERTS: bool = os.getenv('VALIDATE_CERTS')

    # Mr Developer
    DEFAULT_VAT_RATE: Decimal = Decimal(os.getenv('DEFAULT_VAT_RATE', Decimal('0.21')))
    BARCODE_LENGTH: int = int(os.getenv('BARCODE_LENGTH', 30))

    class Config:
        env_file = '.env'


class ProdConfig(BaseConfig):
    DEBUG: bool = False


class DevConfig(BaseConfig):
    DEBUG: bool = True


class TestConfig(BaseConfig):
    DEBUG: bool = True

    class Config:
        env_file = '.env.test'


@lru_cache
def get_settings():
    env = os.getenv('ENVIRONMENT', 'development')

    if env == 'production':
        return ProdConfig()
    elif env == 'testing':
        # HACK: It's not the best way to import test environment values
        load_dotenv(find_dotenv('.env.test'), override=True)
        return TestConfig()

    return DevConfig()
