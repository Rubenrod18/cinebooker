from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.models import Seat
from app.schemas import seat_schemas
from app.services.seat_service import SeatService

router = APIRouter(prefix='/seats', tags=['seats'])


@router.post(
    '/',
    summary='Creates a new Seat',
    status_code=status.HTTP_201_CREATED,
    response_model=seat_schemas.SeatResponseSchema,
    responses={
        201: {
            'description': 'Seat created',
            'content': {
                'application/json': {
                    'schema': {'SeatSchema': {'$ref': '#/components/schemas/SeatResponseSchema'}},
                }
            },
        },
    },
)
@inject
def create_seat_route(
    payload: seat_schemas.SeatCreateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    seat_service: Annotated[SeatService, Depends(Provide[ServiceDIContainer.seat_service])],
) -> Seat:
    seat = seat_service.create(**payload.model_dump())
    session.commit()
    return seat


@router.get(
    '/{seat_id}',
    summary='Returns the Seat data',
    response_model=seat_schemas.SeatResponseSchema,
    responses={
        200: {
            'description': 'Seat data',
        },
        404: {
            'description': 'Seat not found',
        },
    },
)
@inject
def get_seat_details_route(params: seat_schemas.SeatIdRequestSchema = Depends()) -> Seat:
    return params.seat


@router.get(
    '/',
    summary='Returns a list of Seat data',
    response_model=list[seat_schemas.SeatResponseSchema],
    responses={
        200: {
            'description': 'A list of Seat data',
        },
        404: {
            'description': 'Seat not found',
        },
    },
)
@inject
def get_seat_list_route(
    seat_service: Annotated[SeatService, Depends(Provide[ServiceDIContainer.seat_service])],
    page_number: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=20),
) -> list[Seat]:
    return seat_service.get(page_number=page_number, items_per_page=items_per_page)


@router.patch(
    '/{seat_id}',
    summary='Update a Seat',
    response_model=seat_schemas.SeatResponseSchema,
    responses={
        200: {
            'description': 'Returns an updated Seat',
        },
        404: {
            'description': 'Seat not found',
        },
    },
)
@inject
def update_seat_route(
    payload: seat_schemas.SeatUpdateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    seat_service: Annotated[SeatService, Depends(Provide[ServiceDIContainer.seat_service])],
    params: seat_schemas.SeatIdRequestSchema = Depends(),
) -> Seat:
    seat = seat_service.update(params.seat, **payload.model_dump(exclude_unset=True))
    session.commit()
    return seat


@router.delete(
    '/{seat_id}',
    summary='Delete a Seat',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            'description': 'Seat not found',
        },
    },
)
@inject
def delete_seat_route(
    seat_service: Annotated[SeatService, Depends(Provide[ServiceDIContainer.seat_service])],
    params: seat_schemas.SeatIdRequestSchema = Depends(),
) -> None:
    seat_service.delete(params.seat)
    return None
