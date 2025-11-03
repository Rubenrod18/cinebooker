from sqlmodel import Session

from app.models import Payment
from app.models.payment import PaymentStatus
from app.repositories.payment_repository import PaymentRepository
from app.services import core


class PaymentService(
    core.AbstractCreateService,
    core.FindByIdMixin,
    core.AbstractUpdateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        payment_repository: PaymentRepository | None = None,
    ):
        super().__init__(repository=payment_repository or PaymentRepository(session))

    def create(self, **kwargs) -> Payment:
        kwargs['status'] = kwargs.get('status', PaymentStatus.PENDING)
        return self.repository.create(**kwargs)

    def update(self, record, **kwargs) -> Payment:
        return self.repository.update(record, **kwargs)

    def completed(self, record, **kwargs) -> Payment:
        kwargs['status'] = PaymentStatus.COMPLETED
        return self.update(record, **kwargs)

    def cancelled(self, record, **kwargs) -> Payment:
        kwargs['status'] = PaymentStatus.CANCELLED
        return self.update(record, **kwargs)

    def failed(self, record, **kwargs) -> Payment:
        kwargs['status'] = PaymentStatus.FAILED
        return self.update(record, **kwargs)

    def find_by_provider_payment_id(self, provider_payment_id: str) -> Payment | None:
        return self.repository.find_by_provider_payment_id(provider_payment_id)
