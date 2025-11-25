from fastapi import FastAPI

import extensions
from app.routers import get_routers


def _register_routers(app: FastAPI) -> None:
    for router in get_routers():
        app.include_router(router)


def create_app() -> FastAPI:
    app = FastAPI(
        title='Cinebooker API',
    )

    extensions.init_app(app)
    _register_routers(app)

    return app
