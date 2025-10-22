from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.models import BookingSeat
from app.schemas import booking_seat_schemas
from app.services.booking_seat_service import BookingSeatService

router = APIRouter(prefix='/booking-seats', tags=['booking-seats'])


@router.post(
    '/',
    summary='Creates a new BookingSeat',
    status_code=status.HTTP_201_CREATED,
    response_model=booking_seat_schemas.BookingSeatResponseSchema,
    responses={
        201: {
            'description': 'BookingSeat created',
            'content': {
                'application/json': {
                    'schema': {'BookingSeatSchema': {'$ref': '#/components/schemas/BookingSeatResponseSchema'}},
                }
            },
        },
    },
)
@inject
def create_booking_seat_route(
    payload: booking_seat_schemas.BookingSeatCreateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    booking_seat_service: Annotated[BookingSeatService, Depends(Provide[ServiceDIContainer.booking_seat_service])],
) -> BookingSeat:
    booking_seat = booking_seat_service.create(**payload.model_dump())
    session.commit()
    return booking_seat


@router.get(
    '/{booking_seat_id}',
    summary='Returns the BookingSeat data',
    response_model=booking_seat_schemas.BookingSeatResponseSchema,
    responses={
        200: {
            'description': 'BookingSeat data',
        },
        404: {
            'description': 'BookingSeat not found',
        },
    },
)
@inject
def get_booking_seat_details_route(params: booking_seat_schemas.BookingSeatIdRequestSchema = Depends()) -> BookingSeat:
    return params.booking_seat


@router.get(
    '/',
    summary='Returns a list of BookingSeat data',
    response_model=list[booking_seat_schemas.BookingSeatResponseSchema],
    responses={
        200: {
            'description': 'A list of BookingSeat data',
        },
        404: {
            'description': 'BookingSeat not found',
        },
    },
)
@inject
def get_booking_seat_list_route(
    booking_seat_service: Annotated[BookingSeatService, Depends(Provide[ServiceDIContainer.booking_seat_service])],
    page_number: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=20),
) -> list[BookingSeat]:
    return booking_seat_service.get(page_number=page_number, items_per_page=items_per_page)


@router.patch(
    '/{booking_seat_id}',
    summary='Update a BookingSeat',
    response_model=booking_seat_schemas.BookingSeatResponseSchema,
    responses={
        200: {
            'description': 'Returns an updated BookingSeat',
        },
        404: {
            'description': 'BookingSeat not found',
        },
    },
)
@inject
def update_booking_seat_route(
    payload: booking_seat_schemas.BookingSeatUpdateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    booking_seat_service: Annotated[BookingSeatService, Depends(Provide[ServiceDIContainer.booking_seat_service])],
    params: booking_seat_schemas.UpdateBookingSeatIdRequestSchema = Depends(),
) -> BookingSeat:
    booking_seat = booking_seat_service.update(params.booking_seat, **payload.model_dump(exclude_unset=True))
    session.add(booking_seat)
    session.commit()
    return booking_seat
