import logging
import os
import typing as t

import requests

from app.utils.constants import BaseEnum

logger = logging.getLogger(__name__)


class PayPalOrderStatus(BaseEnum):
    CREATED = 'CREATED'


class PayPalWebhookVerificationStatus(BaseEnum):
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCCESS'


class PayPalIntent(BaseEnum):
    """Enumeration of possible payment intents for a PayPal order.

    The `intent` defines how the payment should be processed after the order
    is created — either captured immediately or authorized for later capture.

    Attributes
    ----------
    CAPTURE : str
        The merchant intends to capture payment immediately after the
        customer approves the order. Funds are transferred right away,
        and the payment is considered complete.

        Example
        -------
        A buyer purchases a product, and PayPal immediately captures
        the funds when the order is approved.

    AUTHORIZE : str
        The merchant intends to authorize a payment and place funds
        on hold after the customer approves the order. The authorized
        amount can be captured later, typically within three days, but
        remains valid for up to 29 days.

        Note
        ----
        - After the three-day honor period, the authorization expires
          and a new authorization is required.
        - This intent is **not supported** when there is more than one
          `purchase_unit` in the order.

        Example
        -------
        A hotel pre-authorizes payment at booking and captures the funds
        later at check-in.

    """

    CAPTURE = 'CAPTURE'
    AUTHORIZE = 'AUTHORIZE'


class PayPalEventType(BaseEnum):
    """Enumeration of PayPal webhook event types related to payment success and failure.

    Each constant represents a specific event name that PayPal sends to your webhook
    endpoint. These events help track the lifecycle of a payment from authorization
    to capture, including potential failure or reversal scenarios.

    Attributes
    ----------
    PAYMENT_CAPTURE_COMPLETED : str
        Triggered when a payment capture has been successfully completed.
        Indicates that the funds have been successfully transferred from the buyer
        to the seller. This confirms that the payment is fully paid.

        Example:
            - The order is captured successfully after approval.

    PAYMENT_CAPTURE_DENIED : str
        Triggered when a capture request is explicitly denied by PayPal or the payer's
        financial institution. This indicates that the capture cannot proceed.

        Example:
            - PayPal denies the capture because of a compliance or risk issue.

    """

    PAYMENT_CAPTURE_COMPLETED = 'PAYMENT.CAPTURE.COMPLETED'
    PAYMENT_CAPTURE_DENIED = 'PAYMENT.CAPTURE.DENIED'


class PayPalProvider:
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        webhook_id: str | None = None,
        sandbox: bool | None = None,
    ) -> None:
        self.client_id = client_id or os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('PAYPAL_CLIENT_SECRET')
        self.webhook_id = webhook_id or os.getenv('PAYPAL_WEBHOOK_ID')
        self.sandbox = sandbox or os.getenv('PAYPAL_SANDBOX')
        self.api_base = 'https://api-m.sandbox.paypal.com' if self.sandbox else 'https://api-m.paypal.com'

    def get_access_token(self) -> dict[str, t.Any]:
        resp = requests.post(
            f'{self.api_base}/v1/oauth2/token',
            data={'grant_type': 'client_credentials'},
            auth=(self.client_id, self.client_secret),
            headers={'Accept': 'application/json'},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def create_order(self, payload: dict[str, t.Any]) -> dict[str, t.Any]:
        token_json = self.get_access_token()
        access_token = token_json['access_token']
        try:
            resp = requests.post(
                f'{self.api_base}/v2/checkout/orders',
                json=payload,
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as exc:
            logger.exception(exc.response.text)
            raise exc from exc

    def verify_webhook_signature(
        self,
        transmission_id: str,
        transmission_time: str,
        cert_url: str,
        auth_algo: str,
        transmission_sig: str,
        webhook_event: dict,
        webhook_id: str | None = None,
    ) -> dict:
        webhook_id = webhook_id or self.webhook_id
        token_json = self.get_access_token()
        access_token = token_json['access_token']
        resp = requests.post(
            f'{self.api_base}/v1/notifications/verify-webhook-signature',
            json={
                'transmission_id': transmission_id,
                'transmission_time': transmission_time,
                'cert_url': cert_url,
                'auth_algo': auth_algo,
                'transmission_sig': transmission_sig,
                'webhook_id': webhook_id,
                'webhook_event': webhook_event,
            },
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
