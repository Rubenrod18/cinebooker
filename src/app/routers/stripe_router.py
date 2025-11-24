import logging
import os
from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette import status

from app.di_container import ServiceDIContainer
from app.models.payment import PaymentProvider
from app.providers.stripe_provider import StripeEventType, StripeProvider
from app.schemas import payment_schemas, stripe_schemas
from app.services.booking_service import BookingService
from app.services.invoice_service import InvoiceService
from app.services.payment_service import PaymentService

router = APIRouter(prefix='/stripe', tags=['stripe'])
logger = logging.getLogger(__name__)


@router.post(
    '/session',
    summary='Creates a new Stripe checkout session',
    status_code=status.HTTP_201_CREATED,
    response_model=stripe_schemas.CheckoutSessionResponseSchema,
    responses={
        201: {
            'description': 'new Stripe checkout session created',
            'content': {
                'application/json': {
                    'schema': {
                        'CheckoutSessionResponseSchema': {'$ref': '#/components/schemas/CheckoutSessionResponseSchema'}
                    },
                }
            },
        },
    },
)
@inject
def create_checkout_session_route(
    payload: payment_schemas.BookingIdRequestSchema,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    booking_service: Annotated[BookingService, Depends(Provide[ServiceDIContainer.booking_service])],
    payment_service: Annotated[PaymentService, Depends(Provide[ServiceDIContainer.payment_service])],
) -> dict:
    # QUESTION: Should I check if there are more than one payment with status pending_payment?
    payment = payment_service.create(
        **{
            'booking_id': payload.booking.id,
            'provider': PaymentProvider.STRIPE.value,
            'amount': payload.booking.invoice.total_price,
            'currency': payload.booking.invoice.currency,
        }
    )
    stripe_checkout_session = booking_service.create_stripe_checkout_session(payload.booking, payment)
    session.commit()
    return {'url': stripe_checkout_session.url}


@router.post('/webhook', summary='Verify the callback of the Stripe', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def create_showtime_route(
    request: Request,
    session: Annotated[Session, Depends(Provide[ServiceDIContainer.session])],
    stripe_provider: Annotated[StripeProvider, Depends(Provide[ServiceDIContainer.stripe_provider])],
    booking_service: Annotated[BookingService, Depends(Provide[ServiceDIContainer.booking_service])],
    payment_service: Annotated[PaymentService, Depends(Provide[ServiceDIContainer.payment_service])],
    invoice_service: Annotated[InvoiceService, Depends(Provide[ServiceDIContainer.invoice_service])],
) -> None:
    # NOTE: await is required because request.body() is async and must be awaited to get the actual data
    payload = await request.body()

    event = stripe_provider.verify_webhook(
        payload, sig_header=request.headers.get('Stripe-Signature'), webhook_secret=os.getenv('STRIPE_WEBHOOK_SECRET')
    ).to_dict()

    if event['type'] == StripeEventType.PAYMENT_INTENT_SUCCEEDED.value:
        intent = event['data']['object']
        payment_id = intent.get('metadata', {}).get('payment_id')

        payment = payment_service.find_by_id(payment_id)

        if not payment:
            raise HTTPException(status_code=404, detail='Payment not found')

        payment_service.completed(payment, **{'provider_payment_id': intent.get('id'), 'provider_metadata': None})
        booking_service.confirmed(payment.booking)
        invoice_service.paid(payment.booking.invoice)
        session.commit()
        logger.info('✅ Payment succeeded!')
    elif event['type'] == StripeEventType.PAYMENT_INTENT_FAILED.value:
        intent = event['data']['object']
        payment_id = intent.get('metadata', {}).get('payment_id')
        error_message = intent['last_payment_error']['message'] if intent.get('last_payment_error') else None

        payment = payment_service.find_by_id(payment_id)

        if not payment:
            raise HTTPException(status_code=404, detail='Payment not found')

        payment_service.failed(
            payment, **{'provider_payment_id': intent.get('id'), 'provider_metadata': {'error_message': error_message}}
        )
        session.commit()
        logger.warning('❌ Payment failed!')
