from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.models import Screen
from app.schemas import screen_schemas
from app.services.screen_service import ScreenService

router = APIRouter(prefix='/screens', tags=['screens'])


@router.post(
    '/',
    summary='Creates a new Screen',
    status_code=status.HTTP_201_CREATED,
    response_model=screen_schemas.ScreenResponseSchema,
    responses={
        201: {
            'description': 'Screen created',
            'content': {
                'application/json': {
                    'schema': {'ScreenSchema': {'$ref': '#/components/schemas/ScreenResponseSchema'}},
                }
            },
        },
    },
)
@inject
def create_screen_route(
    payload: screen_schemas.ScreenCreateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    screen_service: Annotated[ScreenService, Depends(Provide[ServiceDIContainer.screen_service])],
) -> Screen:
    screen = screen_service.create(**payload.model_dump())
    session.commit()
    return screen


@router.get(
    '/{screen_id}',
    summary='Returns the Screen data',
    response_model=screen_schemas.ScreenResponseSchema,
    responses={
        200: {
            'description': 'Screen data',
        },
        404: {
            'description': 'Screen not found',
        },
    },
)
@inject
def get_screen_details_route(params: screen_schemas.ScreenIdRequestSchema = Depends()) -> Screen:
    return params.screen


@router.get(
    '/',
    summary='Returns a list of Screen data',
    response_model=list[screen_schemas.ScreenResponseSchema],
    responses={
        200: {
            'description': 'A list of Screen data',
        },
        404: {
            'description': 'Screen not found',
        },
    },
)
@inject
def get_screen_list_route(
    screen_service: Annotated[ScreenService, Depends(Provide[ServiceDIContainer.screen_service])],
    page_number: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=20),
) -> list[Screen]:
    return screen_service.get(page_number=page_number, items_per_page=items_per_page)


@router.patch(
    '/{screen_id}',
    summary='Update a Screen',
    response_model=screen_schemas.ScreenResponseSchema,
    responses={
        200: {
            'description': 'Returns an updated Screen',
        },
        404: {
            'description': 'Screen not found',
        },
    },
)
@inject
def update_screen_route(
    payload: screen_schemas.ScreenUpdateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    screen_service: Annotated[ScreenService, Depends(Provide[ServiceDIContainer.screen_service])],
    params: screen_schemas.ScreenIdRequestSchema = Depends(),
) -> Screen:
    screen = screen_service.update(params.screen, **payload.model_dump(exclude_unset=True))
    session.commit()
    return screen


@router.delete(
    '/{screen_id}',
    summary='Delete a Screen',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            'description': 'Screen not found',
        },
    },
)
@inject
def delete_screen_route(
    screen_service: Annotated[ScreenService, Depends(Provide[ServiceDIContainer.screen_service])],
    params: screen_schemas.ScreenIdRequestSchema = Depends(),
) -> None:
    screen_service.delete(params.screen)
    return None
