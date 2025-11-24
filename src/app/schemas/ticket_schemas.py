from datetime import datetime

from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, field_validator, PrivateAttr
from sqlalchemy.orm import joinedload

from app.di_container import ServiceDIContainer
from app.exceptions import NotFoundException, UnprocessableEntityException
from app.models import Booking, BookingSeat, Ticket
from app.models.booking import BookingStatus
from app.models.ticket import TicketStatus
from app.repositories.ticket_repository import TicketRepository


class TicketBarcodeValueSchema(BaseModel):
    barcode_value: str
    _ticket: Ticket | None = PrivateAttr(default=None)

    @field_validator('barcode_value')
    @classmethod
    @inject
    def validate_barcode_value(
        cls, barcode_value: str, ticket_repository: TicketRepository = Provide[ServiceDIContainer.ticket_repository]
    ) -> str:
        ticket = ticket_repository.find_one(
            options=(joinedload(Ticket.booking_seat).joinedload(BookingSeat.booking).joinedload(Booking.showtime),),
            filters=(Ticket.barcode_value == barcode_value,),
            joins=((BookingSeat, 'inner'),),
        )

        if not ticket:
            raise NotFoundException(description='Ticket not found')

        if ticket.booking_seat.booking.status != BookingStatus.CONFIRMED:
            raise UnprocessableEntityException(description='Unpaid Booking')

        if ticket.status == TicketStatus.REDEEMED:
            raise UnprocessableEntityException(description='Ticket already used')

        if ticket.booking_seat.booking.showtime.start_time < datetime.now():  # NOTE: UTC not required in datetime.now
            raise UnprocessableEntityException(description='Showtime already started or expired')

        cls._ticket = ticket
        return barcode_value

    @property
    def ticket(self) -> Ticket:
        return self._ticket
