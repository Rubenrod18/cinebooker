from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.models import Customer
from app.schemas import customer_schemas
from app.services.auth_user_service import AuthUserService
from app.services.customer_service import CustomerService

router = APIRouter(prefix='/customers', tags=['customers'])


@router.post(
    '/',
    summary='Creates a new customer',
    status_code=status.HTTP_201_CREATED,
    response_model=customer_schemas.CustomerResponseSchema,
    responses={
        201: {
            'description': 'Customer created',
            'content': {
                'application/json': {
                    'schema': {'CustomerSchema': {'$ref': '#/components/schemas/CustomerResponseSchema'}},
                }
            },
        },
    },
)
@inject
def create_customer(
    payload: customer_schemas.CustomerCreateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    auth_user_service: Annotated[AuthUserService, Depends(Provide[ServiceDIContainer.auth_user_service])],
    customer_service: Annotated[CustomerService, Depends(Provide[ServiceDIContainer.customer_service])],
) -> Customer:
    auth_user_fields, customer_fields = payload['auth_user'], payload['customer']

    with session.begin():
        auth_user = auth_user_service.create(**auth_user_fields)
        customer = customer_service.create(auth_user_id=auth_user.id, **customer_fields)

    return customer
