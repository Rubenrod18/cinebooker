from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.models import Movie
from app.schemas import movie_schemas
from app.services.movie_service import MovieService

router = APIRouter(prefix='/movies', tags=['movies'])


@router.post(
    '/',
    summary='Creates a new Movie',
    status_code=status.HTTP_201_CREATED,
    response_model=movie_schemas.MovieResponseSchema,
    responses={
        201: {
            'description': 'Movie created',
            'content': {
                'application/json': {
                    'schema': {'MovieSchema': {'$ref': '#/components/schemas/MovieResponseSchema'}},
                }
            },
        },
    },
)
@inject
def create_movie_route(
    payload: movie_schemas.MovieCreateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    movie_service: Annotated[MovieService, Depends(Provide[ServiceDIContainer.movie_service])],
) -> Movie:
    movie = movie_service.create(**payload.model_dump())
    session.commit()
    return movie


@router.get(
    '/{movie_id}',
    summary='Returns the Movie data',
    response_model=movie_schemas.MovieResponseSchema,
    responses={
        200: {
            'description': 'Movie data',
        },
        404: {
            'description': 'Movie not found',
        },
    },
)
@inject
def get_movie_details_route(params: movie_schemas.MovieIdRequestSchema = Depends()) -> Movie:
    return params.movie


@router.get(
    '/',
    summary='Returns a list of Movie data',
    response_model=list[movie_schemas.MovieResponseSchema],
    responses={
        200: {
            'description': 'A list of Movie data',
        },
        404: {
            'description': 'Movie not found',
        },
    },
)
@inject
def get_movie_list_route(
    movie_service: Annotated[MovieService, Depends(Provide[ServiceDIContainer.movie_service])],
    page_number: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=20),
) -> list[Movie]:
    return movie_service.get(page_number=page_number, items_per_page=items_per_page)


@router.patch(
    '/{movie_id}',
    summary='Update a Movie',
    response_model=movie_schemas.MovieResponseSchema,
    responses={
        200: {
            'description': 'Returns an updated Movie',
        },
        404: {
            'description': 'Movie not found',
        },
    },
)
@inject
def update_movie_route(
    payload: movie_schemas.MovieUpdateSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    movie_service: Annotated[MovieService, Depends(Provide[ServiceDIContainer.movie_service])],
    params: movie_schemas.MovieIdRequestSchema = Depends(),
) -> Movie:
    movie = movie_service.update(params.movie, **payload.model_dump(exclude_unset=True))
    session.commit()
    return movie


@router.delete(
    '/{movie_id}',
    summary='Delete a Movie',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            'description': 'Movie not found',
        },
    },
)
@inject
def delete_movie_route(
    movie_service: Annotated[MovieService, Depends(Provide[ServiceDIContainer.movie_service])],
    params: movie_schemas.MovieIdRequestSchema = Depends(),
) -> None:
    movie_service.delete(params.movie)
    return None
