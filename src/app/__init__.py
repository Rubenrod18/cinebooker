from fastapi import FastAPI

from app.routers import get_routers


def _register_routers(app: FastAPI) -> None:
    for router in get_routers():
        app.include_router(router)


def _init_python_dependency_injector(app: FastAPI) -> None:
    from app.di_container import ServiceDIContainer  # pylint: disable=import-outside-toplevel

    container = ServiceDIContainer()
    app.container = container


def create_app() -> FastAPI:
    app = FastAPI(
        title='Cinebooker API',
    )

    _init_python_dependency_injector(app)
    _register_routers(app)

    return app
