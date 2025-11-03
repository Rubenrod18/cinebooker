import logging
from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from app.di_container import ServiceDIContainer
from app.models.payment import PaymentProvider
from app.providers import paypal_provider
from app.schemas import payment_schemas, paypal_schemas
from app.services.booking_service import BookingService
from app.services.payment_service import PaymentService

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


@router.post('/webhook', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def paypal_webhook(
    request: Request,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    booking_service: Annotated[BookingService, Depends(Provide[ServiceDIContainer.booking_service])],
    payment_service: Annotated[PaymentService, Depends(Provide[ServiceDIContainer.payment_service])],
    paypal_transmission_id: str | None = Header(None, alias='PAYPAL-TRANSMISSION-ID'),
    paypal_transmission_time: str | None = Header(None, alias='PAYPAL-TRANSMISSION-TIME'),
    paypal_cert_url: str | None = Header(None, alias='PAYPAL-CERT-URL'),
    paypal_auth_algo: str | None = Header(None, alias='PAYPAL-AUTH-ALGO'),
    paypal_transmission_sig: str | None = Header(None, alias='PAYPAL-TRANSMISSION-SIG'),
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
            # TODO: Pending to mark the invoice as paid  # pylint: disable=fixme
            logger.info('✅ Payment succeeded!')
        else:
            payment_service.cancelled(payment, **{'provider_metadata': resource})
            booking_service.cancelled(payment.booking)
            logger.warning('❌ Payment cancelled!')

        session.commit()
