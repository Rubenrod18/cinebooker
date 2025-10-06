from typing import Any

from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from app.models import Movie
from app.repositories import core


class MovieRepository(
    core.AbstractBaseRepository,
    core.AbstractCreateRepository,
    core.AbstractFindByIdRepository,
    core.AbstractGetRepository,
    core.AbstractUpdateRepository,
    core.AbstractDeleteRepository,
):
    def __init__(self, session: Session):
        super().__init__(model=Movie, session=session)

    def create(self, **kwargs) -> Movie:
        movie = self.model(**kwargs)
        self.session.add(movie)
        self.session.flush()
        return movie

    def find_by_id(self, record_id: Any) -> SQLModel:
        return (
            self.session.query(self.model)
            .filter(
                self.model.id == record_id,
                self.model.inactive_at.is_(None),
            )
            .first()
        )

    def get(self, **kwargs) -> list[SQLModel]:
        page_number = int(kwargs.get('page_number', 1)) - 1
        items_per_page = int(kwargs.get('items_per_page', 10))
        order = kwargs.get('order', [self.model.created_at.asc()])

        return list(
            self.session.query(self.model)
            .filter(self.model.inactive_at.is_(None))
            .order_by(*order)
            .offset(page_number * items_per_page)
            .limit(items_per_page)
        )

    def update(self, record, **kwargs) -> SQLModel | None:
        for field, value in kwargs.items():
            setattr(record, field, value)

        return record

    def delete(self, record, **kwargs) -> SQLModel | None:
        record.inactive()
        return record
