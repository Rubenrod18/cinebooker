import sqlalchemy as sa
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from app.di_container import ServiceDIContainer
from database import SQLDatabase

router = APIRouter()


@router.get('/')
def welcome_route():
    return {'message': 'Welcome to CineBooker API!'}


@router.get('/health')
@inject
def health_check_route(sql_db: SQLDatabase = Depends(Provide[ServiceDIContainer.sql_db])):
    try:
        with sql_db.session() as session:
            session.execute(sa.text('SELECT 1'))
        return {'message': 'Connected to PostgreSQL'}
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {'error': str(e)}
