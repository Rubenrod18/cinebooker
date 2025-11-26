import asyncio

import jinja2
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.repositories.payment_repository import PaymentRepository
from app.utils import generate_qr_base64
from app.utils.constants import DEFAULT_DATETIME_FORMAT
from config import get_settings
from database import get_session

from .celery import celery


@celery.task()
def send_email_to_customer_task(payment_id):
    payment_repository = PaymentRepository(session=get_session())
    payment = payment_repository.find_by_id(payment_id)
    booking = payment.booking

    ticket_data = [
        {
            'qr_base64': f'data:image/png;base64,{generate_qr_base64(booking_seat.ticket.barcode_value)}',
            'row': booking_seat.seat.row,
            'number': booking_seat.seat.number,
            'barcode_value': booking_seat.ticket.barcode_value,
        }
        for booking_seat in booking.booking_seats
    ]
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/mails'))

    template = env.get_template('tickets.html')
    data = {
        'movie_title': booking.showtime.movie.title,
        'show_datetime': booking.showtime.start_time.strftime(DEFAULT_DATETIME_FORMAT),
        'screen_name': booking.showtime.screen.name,
        'payment_datetime': payment.created_at.strftime(DEFAULT_DATETIME_FORMAT),
        'booking_id': booking.id.hex,
        'tickets': ticket_data,
    }
    rendered_html = template.render(**data)
    message = MessageSchema(
        subject='FastAPI-Mail module',
        recipients=['hello_world@mail.com'],
        body=rendered_html,
        subtype=MessageType.html,
    )

    settings = get_settings()
    fastapi_mail = FastMail(
        ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        )
    )
    # NOTE: Celery tasks run synchronously and have no event loop.
    #       FastAPI-Mail is async so we must run it inside our own loop.
    asyncio.run(fastapi_mail.send_message(message))
