from typing import Annotated

import sqlalchemy as sa
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.di_container import ServiceDIContainer
from extensions import get_fastapi_mail

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


@router.post('/email')
async def send_email_route(fastapi_mail=Depends(get_fastapi_mail)):
    message = MessageSchema(
        subject='FastAPI-Mail module',
        recipients=['hello_world@mail.com'],
        body="""<p>Hi this test mail, thanks for using Fastapi-mail</p>""",
        subtype=MessageType.html,
    )
    await fastapi_mail.send_message(message)

    return JSONResponse(status_code=200, content={'message': 'email has been sent'})
