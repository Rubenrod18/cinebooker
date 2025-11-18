from decimal import Decimal

from sqlmodel import Session, SQLModel

from app.models import Discount
from app.repositories.discount_repository import DiscountRepository
from app.services import core


class DiscountService(
    core.AbstractCreateService,
    core.GetMixin,
    core.AbstractUpdateService,
    core.AbstractDeleteService,
):
    def __init__(
        self,
        session: type[Session] = None,
        discount_repository: DiscountRepository | None = None,
    ):
        super().__init__(repository=discount_repository or DiscountRepository(session))

    def create(self, **kwargs) -> Discount:
        return self.repository.create(**kwargs)

    def find_by_code(self, **kwargs) -> Discount:
        return self.repository.find_by_code(**kwargs)

    def update(self, record, **kwargs) -> Discount:
        return self.repository.update(record, **kwargs)

    def delete(self, record, **kwargs) -> SQLModel | None:
        return self.repository.delete(record, **kwargs)

    def apply_discount_to_total_base_price(
        self, total_base_price: Decimal, discount: Discount | None = None
    ) -> Decimal:
        if discount is None:
            return total_base_price

        discounted_price = total_base_price

        if discount.is_percentage:
            discount_amount = total_base_price * (Decimal(discount.amount) / Decimal('100'))
            discounted_price -= discount_amount
        else:
            discounted_price -= Decimal(discount.amount)

        # NOTE: Avoid negative totals
        return max(discounted_price, Decimal('0'))
