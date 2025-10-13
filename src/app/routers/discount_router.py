from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.models import Discount
from app.schemas import discount_schemas
from app.services.discount_service import DiscountService

router = APIRouter(prefix='/discounts', tags=['discounts'])


@router.post(
    '/',
    summary='Creates a new Discount',
    status_code=status.HTTP_201_CREATED,
    response_model=discount_schemas.DiscountResponseSchema,
    responses={
        201: {
            'description': 'Discount created',
            'content': {
                'application/json': {
                    'schema': {'DiscountSchema': {'$ref': '#/components/schemas/DiscountResponseSchema'}},
                }
            },
        },
    },
)
@inject
def create_discount_route(
    payload: discount_schemas.DiscountCreateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    discount_service: Annotated[DiscountService, Depends(Provide[ServiceDIContainer.discount_service])],
) -> Discount:
    discount = discount_service.create(**payload.model_dump())
    session.commit()
    return discount


@router.get(
    '/{discount_code}',
    summary='Returns the Discount data',
    response_model=discount_schemas.DiscountResponseSchema,
    responses={
        200: {
            'description': 'Discount data',
        },
        404: {
            'description': 'Discount not found',
        },
    },
)
@inject
def get_discount_details_route(params: discount_schemas.DiscountCodeRequestSchema = Depends()) -> Discount:
    return params.discount


@router.get(
    '/',
    summary='Returns a list of Discount data',
    response_model=list[discount_schemas.DiscountResponseSchema],
    responses={
        200: {
            'description': 'A list of Discount data',
        },
        404: {
            'description': 'Discount not found',
        },
    },
)
@inject
def get_discount_list_route(
    discount_service: Annotated[DiscountService, Depends(Provide[ServiceDIContainer.discount_service])],
    page_number: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=20),
) -> list[Discount]:
    return discount_service.get(page_number=page_number, items_per_page=items_per_page)


@router.patch(
    '/{discount_code}',
    summary='Update a Discount',
    response_model=discount_schemas.DiscountResponseSchema,
    responses={
        200: {
            'description': 'Returns an updated Discount',
        },
        404: {
            'description': 'Discount not found',
        },
    },
)
@inject
def update_discount_route(
    payload: discount_schemas.DiscountUpdateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    discount_service: Annotated[DiscountService, Depends(Provide[ServiceDIContainer.discount_service])],
    params: discount_schemas.DiscountCodeRequestSchema = Depends(),
) -> Discount:
    discount = discount_service.update(params.discount, **payload.model_dump(exclude_unset=True))
    session.commit()
    return discount


@router.delete(
    '/{discount_code}',
    summary='Delete a Discount',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            'description': 'Discount not found',
        },
    },
)
@inject
def delete_discount_route(
    discount_service: Annotated[DiscountService, Depends(Provide[ServiceDIContainer.discount_service])],
    params: discount_schemas.DiscountCodeRequestSchema = Depends(),
) -> None:
    discount_service.delete(params.discount)
    return None
