import base64
import logging
from io import BytesIO
from typing import Annotated

import qrcode
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi_mail import MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from app.di_container import ServiceDIContainer
from app.models.payment import PaymentProvider
from app.providers import paypal_provider
from app.schemas import payment_schemas, paypal_schemas
from app.services.booking_service import BookingService
from app.services.invoice_service import InvoiceService
from app.services.payment_service import PaymentService
from app.utils.constants import DEFAULT_DATETIME_FORMAT
from extensions import get_fastapi_mail

router = APIRouter(prefix='/paypal', tags=['paypal'])
logger = logging.getLogger(__name__)


@router.post(
    '/create-payment',
    summary='Creates a new Paypal payment',
    status_code=status.HTTP_201_CREATED,
    response_model=paypal_schemas.CreatePaymentResponseSchema,
    responses={
        201: {
            'description': 'new Paypal payment created',
            'content': {
                'application/json': {
                    'schema': {
                        'CreatePaymentResponseSchema': {'$ref': '#/components/schemas/CreatePaymentResponseSchema'}
                    },
                }
            },
        },
    },
)
@inject
def create_payment_route(
    payload: payment_schemas.BookingIdRequestSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    booking_service: Annotated[BookingService, Depends(Provide[ServiceDIContainer.booking_service])],
    payment_service: Annotated[PaymentService, Depends(Provide[ServiceDIContainer.payment_service])],
) -> paypal_schemas.CreatePaymentResponseSchema:
    payment = payment_service.create(
        **{
            'booking_id': payload.booking.id,
            'provider': PaymentProvider.PAYPAL.value,
            'amount': payload.booking.invoice.total_price,
            'currency': payload.booking.invoice.currency,
        }
    )
    order = booking_service.create_paypal_order(payload.booking)

    links = order.get('links', [])
    approve_link = None
    for link in links:
        if link.get('rel') == 'approve':
            approve_link = link.get('href')
            break

    if not approve_link:
        raise HTTPException(status_code=500, detail='No approve link returned by PayPal')

    payment_service.update(payment, **{'provider_payment_id': order['id']})
    session.commit()
    return paypal_schemas.CreatePaymentResponseSchema(order_id=order['id'], approve_link=approve_link)


async def generate_qr_base64(data: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer)
    qr_bytes = buffer.getvalue()
    return base64.b64encode(qr_bytes).decode('utf-8')


# HACK: Move this logic to a Celery task
async def send_email_to_customer(fastapi_mail, payment):
    booking = payment.booking
    ticket_data = [
        {
            'qr_base64': f'data:image/png;base64,{await generate_qr_base64(booking_seat.ticket.barcode_value)}',
            'row': booking_seat.seat.row,
            'number': booking_seat.seat.number,
            'barcode_value': booking_seat.ticket.barcode_value,
        }
        for booking_seat in booking.booking_seats
    ]
    env = Environment(loader=FileSystemLoader('templates/mails'))
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
    await fastapi_mail.send_message(message)


@router.post('/webhook', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def paypal_webhook(
    request: Request,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    booking_service: Annotated[BookingService, Depends(Provide[ServiceDIContainer.booking_service])],
    payment_service: Annotated[PaymentService, Depends(Provide[ServiceDIContainer.payment_service])],
    invoice_service: Annotated[InvoiceService, Depends(Provide[ServiceDIContainer.invoice_service])],
    paypal_transmission_id: str | None = Header(None, alias='PAYPAL-TRANSMISSION-ID'),
    paypal_transmission_time: str | None = Header(None, alias='PAYPAL-TRANSMISSION-TIME'),
    paypal_cert_url: str | None = Header(None, alias='PAYPAL-CERT-URL'),
    paypal_auth_algo: str | None = Header(None, alias='PAYPAL-AUTH-ALGO'),
    paypal_transmission_sig: str | None = Header(None, alias='PAYPAL-TRANSMISSION-SIG'),
    fastapi_mail=Depends(get_fastapi_mail),
) -> None:
    """Handle PayPal webhooks.

    We verify the signature using PayPal's verify-webhook-signature endpoint.
    Then we process certain events (e.g., PAYMENT.CAPTURE.COMPLETED).

    """
    body = await request.json()

    if not all(
        [paypal_transmission_id, paypal_transmission_time, paypal_cert_url, paypal_auth_algo, paypal_transmission_sig]
    ):
        logger.exception('Missing PayPal headers')
        raise HTTPException(status_code=400, detail='Missing PayPal headers')

    verify_response = booking_service.paypal_provider.verify_webhook_signature(
        transmission_id=paypal_transmission_id,
        transmission_time=paypal_transmission_time,
        cert_url=paypal_cert_url,
        auth_algo=paypal_auth_algo,
        transmission_sig=paypal_transmission_sig,
        webhook_event=body,
    )

    if verify_response.get('verification_status') != 'SUCCESS':
        logger.exception('Invalid webhook signature')
        raise HTTPException(status_code=400, detail='Invalid webhook signature')

    event_type = body.get('event_type')
    resource = body.get('resource', {})

    if event_type in [
        paypal_provider.PayPalEventType.PAYMENT_CAPTURE_COMPLETED.value,
        paypal_provider.PayPalEventType.PAYMENT_CAPTURE_DENIED.value,
    ]:
        order_id = resource.get('id')
        payment = payment_service.find_by_provider_payment_id(order_id)
        if not payment:
            # QUESTION: Should I send a notification to Slack or other channel?
            raise HTTPException(status_code=404, detail='Payment not found')

        if event_type == paypal_provider.PayPalEventType.PAYMENT_CAPTURE_COMPLETED.value:
            payment_service.completed(payment, **{'provider_metadata': None})
            booking_service.confirmed(payment.booking)
            invoice_service.paid(payment.booking.invoice)
            logger.info('✅ Payment succeeded!')
            await send_email_to_customer(fastapi_mail, payment)
        else:
            payment_service.cancelled(payment, **{'provider_metadata': resource})
            booking_service.cancelled(payment.booking)
            logger.warning('❌ Payment cancelled!')

        session.commit()
