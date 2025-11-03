from pydantic import BaseModel


class CreatePaymentResponseSchema(BaseModel):
    order_id: str
    approve_link: str
