import os
from decimal import Decimal
from functools import lru_cache

from dotenv import load_dotenv
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


@lru_cache
def get_settings():
    env = os.getenv('ENVIRONMENT', 'development')

    if env == 'production':
        return ProdConfig()
    elif env == 'testing':
        return TestConfig()

    return DevConfig()
