from typing import Any

from sqlalchemy.orm import joinedload, Session
from sqlmodel import SQLModel

from app.models import Booking, Discount, Invoice
from app.repositories import core


class BookingRepository(
    core.AbstractCreateRepository,
    core.AbstractFindByIdRepository,
    core.AbstractGetRepository,
    core.AbstractUpdateRepository,
    core.FindOneMixin,
):
    def __init__(self, session: Session):
        super().__init__(model=Booking, session=session)

    def create(self, **kwargs) -> Booking:
        movie = self.model(**kwargs)
        self.session.add(movie)
        self.session.flush()
        return movie

    def find_by_id(self, record_id: Any) -> SQLModel:
        return self.find_one(filters=(self.model.id == record_id, self.model.expired_at.is_(None)))

    def find_one_with_invoices(self, *filters):
        return self.find_one(
            options=(joinedload(Booking.invoice).joinedload(Invoice.invoice_items),),
            joins=((Invoice, 'inner'),),
            filters=filters,
        )

    def find_one_with_invoices_and_discount(self, *filters):
        return self.find_one(
            options=(joinedload(Booking.invoice).joinedload(Invoice.invoice_items), joinedload(Booking.discount)),
            joins=((Invoice, 'outer'), (Discount, 'outer')),
            filters=filters,
        )

    def find_one_with_seats_and_discount(self, *filters):
        return self.find_one(
            options=(joinedload(Booking.booking_seats), joinedload(Booking.discount)),
            joins=((Discount, 'outer'),),
            filters=filters,
        )

    def find_one_with_invoices_seats_and_discount(self, *filters):
        return self.find_one(
            options=(
                joinedload(Booking.booking_seats),
                joinedload(Booking.invoice).joinedload(Invoice.invoice_items),
                joinedload(Booking.discount),
            ),
            joins=((Invoice, 'inner'), (Discount, 'outer')),
            filters=filters,
        )

    def get(self, **kwargs) -> list[SQLModel]:
        page_number = int(kwargs.get('page_number', 1)) - 1
        items_per_page = int(kwargs.get('items_per_page', 10))
        order = kwargs.get('order', [self.model.created_at.asc()])

        return list(
            self.session.query(self.model)
            .filter(self.model.expired_at.is_(None))
            .order_by(*order)
            .offset(page_number * items_per_page)
            .limit(items_per_page)
        )

    def update(self, record, **kwargs) -> SQLModel | None:
        for field, value in kwargs.items():
            setattr(record, field, value)

        return record
