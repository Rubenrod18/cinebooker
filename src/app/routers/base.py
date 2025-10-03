from typing import Annotated

import sqlalchemy as sa
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.di_container import ServiceDIContainer

router = APIRouter()


@router.get('/')
def welcome_route():
    return {'message': 'Welcome to CineBooker API!'}


@router.get('/health')
@inject
def health_check_route(session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])]):
    try:
        session.execute(sa.text('SELECT 1'))
        return {'message': 'Connected to PostgreSQL'}
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {'error': str(e)}
