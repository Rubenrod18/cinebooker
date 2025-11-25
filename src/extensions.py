from fastapi import FastAPI, Request
from fastapi_mail import ConnectionConfig, FastMail

from app.di_container import settings


def init_app(app: FastAPI) -> None:
    _init_fastapi_mail(app)
    _init_python_dependency_injector(app)


def _init_fastapi_mail(app: FastAPI) -> None:
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    )
    app.state.fastapi_mail = FastMail(conf)


def _init_python_dependency_injector(app: FastAPI) -> None:
    from app.di_container import ServiceDIContainer  # pylint: disable=import-outside-toplevel

    container = ServiceDIContainer()
    app.container = container


def get_fastapi_mail(request: Request):
    return request.app.state.fastapi_mail
