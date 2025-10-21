from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.models import Showtime
from app.schemas import showtime_schemas
from app.services.showtime_service import ShowtimeService

router = APIRouter(prefix='/showtimes', tags=['showtimes'])


@router.post(
    '/',
    summary='Creates a new Showtime',
    status_code=status.HTTP_201_CREATED,
    response_model=showtime_schemas.ShowtimeResponseSchema,
    responses={
        201: {
            'description': 'Showtime created',
            'content': {
                'application/json': {
                    'schema': {'ShowtimeSchema': {'$ref': '#/components/schemas/ShowtimeResponseSchema'}},
                }
            },
        },
    },
)
@inject
def create_showtime_route(
    payload: showtime_schemas.ShowtimeCreateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    showtime_service: Annotated[ShowtimeService, Depends(Provide[ServiceDIContainer.showtime_service])],
) -> Showtime:
    showtime = showtime_service.create(**payload.model_dump())
    session.commit()
    return showtime


@router.get(
    '/{showtime_id}',
    summary='Returns the Showtime data',
    response_model=showtime_schemas.ShowtimeResponseSchema,
    responses={
        200: {
            'description': 'Showtime data',
        },
        404: {
            'description': 'Showtime not found',
        },
    },
)
@inject
def get_showtime_details_route(params: showtime_schemas.ShowtimeIdRequestSchema = Depends()) -> Showtime:
    return params.showtime


@router.get(
    '/',
    summary='Returns a list of Showtime data',
    response_model=list[showtime_schemas.ShowtimeResponseSchema],
    responses={
        200: {
            'description': 'A list of Showtime data',
        },
        404: {
            'description': 'Showtime not found',
        },
    },
)
@inject
def get_showtime_list_route(
    showtime_service: Annotated[ShowtimeService, Depends(Provide[ServiceDIContainer.showtime_service])],
    page_number: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=20),
) -> list[Showtime]:
    return showtime_service.get(page_number=page_number, items_per_page=items_per_page)


@router.patch(
    '/{showtime_id}',
    summary='Update a Showtime',
    response_model=showtime_schemas.ShowtimeResponseSchema,
    responses={
        200: {
            'description': 'Returns an updated Showtime',
        },
        404: {
            'description': 'Showtime not found',
        },
    },
)
@inject
def update_showtime_route(
    payload: showtime_schemas.ShowtimeUpdateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    showtime_service: Annotated[ShowtimeService, Depends(Provide[ServiceDIContainer.showtime_service])],
    params: showtime_schemas.ShowtimeIdRequestSchema = Depends(),
) -> Showtime:
    showtime = showtime_service.update(params.showtime, **payload.model_dump(exclude_unset=True))
    session.add(showtime)
    session.commit()
    return showtime
