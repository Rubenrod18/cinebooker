import os
import typing
from typing import Unpack

import stripe
from fastapi import HTTPException
from starlette import status

from app.utils.constants import BaseEnum

if typing.TYPE_CHECKING:
    from stripe.params.billing_portal import SessionCreateParams


class StripeEventType(BaseEnum):
    PAYMENT_INTENT_SUCCEEDED = 'payment_intent.succeeded'
    PAYMENT_INTENT_FAILED = 'payment_intent.payment_failed'


class StripeProvider:
    def __init__(self, api_key: str | None = None) -> None:
        self.client = stripe
        self.client.api_key = api_key or os.getenv('STRIPE_API_KEY')

    def create_checkout_session(self, **params: Unpack['SessionCreateParams']) -> stripe.checkout.Session:
        return self.client.checkout.Session.create(**params)

    def verify_webhook(
        self, payload: bytes, sig_header: str, webhook_secret: str, tolerance: int = None, api_key: str = None
    ) -> stripe.Event:
        try:
            return self.client.Webhook.construct_event(payload, sig_header, webhook_secret, tolerance, api_key)
        except stripe.SignatureVerificationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid signature') from exc
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
