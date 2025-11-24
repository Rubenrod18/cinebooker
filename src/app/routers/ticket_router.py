from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.schemas import ticket_schemas
from app.services.ticket_service import TicketService

router = APIRouter(prefix='/tickets', tags=['tickets'])


@router.post(
    '/verify',
    summary='Verify if a Ticket is valid and mark the Ticket as redeemed',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            'description': 'Ticket not found',
        },
    },
)
@inject
def post_verify_ticket_route(
    payload: ticket_schemas.TicketBarcodeValueSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    ticket_service: Annotated[TicketService, Depends(Provide[ServiceDIContainer.ticket_service])],
) -> None:
    ticket_service.redeemed(payload.ticket)
    session.commit()
