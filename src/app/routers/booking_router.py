from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.models import Booking
from app.schemas import booking_schemas
from app.services.booking_service import BookingService

router = APIRouter(prefix='/bookings', tags=['bookings'])


@router.post(
    '/',
    summary='Creates a new Booking',
    status_code=status.HTTP_201_CREATED,
    response_model=booking_schemas.BookingResponseSchema,
    responses={
        201: {
            'description': 'Booking created',
            'content': {
                'application/json': {
                    'schema': {'BookingSchema': {'$ref': '#/components/schemas/BookingResponseSchema'}},
                }
            },
        },
    },
)
@inject
def create_booking_route(
    payload: booking_schemas.BookingCreateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    booking_service: Annotated[BookingService, Depends(Provide[ServiceDIContainer.booking_service])],
) -> Booking:
    booking = booking_service.create(**payload.model_dump())
    session.commit()
    return booking


@router.get(
    '/{booking_id}',
    summary='Returns the Booking data',
    response_model=booking_schemas.BookingResponseSchema,
    responses={
        200: {
            'description': 'Booking data',
        },
        404: {
            'description': 'Booking not found',
        },
    },
)
@inject
def get_booking_details_route(params: booking_schemas.BookingIdRequestSchema = Depends()) -> Booking:
    return params.booking


@router.get(
    '/',
    summary='Returns a list of Booking data',
    response_model=list[booking_schemas.BookingResponseSchema],
    responses={
        200: {
            'description': 'A list of Booking data',
        },
        404: {
            'description': 'Booking not found',
        },
    },
)
@inject
def get_booking_list_route(
    booking_service: Annotated[BookingService, Depends(Provide[ServiceDIContainer.booking_service])],
    page_number: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=20),
) -> list[Booking]:
    return booking_service.get(page_number=page_number, items_per_page=items_per_page)


@router.patch(
    '/{booking_id}',
    summary='Update a Booking',
    response_model=booking_schemas.BookingResponseSchema,
    responses={
        200: {
            'description': 'Returns an updated Booking',
        },
        404: {
            'description': 'Booking not found',
        },
    },
)
@inject
def update_booking_route(
    payload: booking_schemas.BookingUpdateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    booking_service: Annotated[BookingService, Depends(Provide[ServiceDIContainer.booking_service])],
    params: booking_schemas.BookingIdRequestSchema = Depends(),
) -> Booking:
    booking = booking_service.update(params.booking, **payload.model_dump(exclude_unset=True))
    session.add(booking)
    session.commit()
    return booking
