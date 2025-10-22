from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session
from sqlmodel import SQLModel


class AbstractBaseRepository(ABC):
    def __init__(self, model: SQLModel, session: Session):
        self.model = model
        self.session = session


class AbstractCreateRepository(ABC):
    @abstractmethod
    def create(self, **kwargs) -> SQLModel:
        raise NotImplementedError


class AbstractUpdateRepository(ABC):
    @abstractmethod
    def update(self, record, **kwargs) -> SQLModel | None:
        raise NotImplementedError


class AbstractDeleteRepository(ABC):
    @abstractmethod
    def delete(self, record, **kwargs) -> SQLModel | None:
        raise NotImplementedError


class AbstractFindOneRepository(ABC):
    @abstractmethod
    def find_one(self, **filters) -> SQLModel | None:
        raise NotImplementedError


class AbstractFindByIdRepository(ABC):
    @abstractmethod
    def find_by_id(self, record_id) -> SQLModel | None:
        raise NotImplementedError


class AbstractGetRepository(ABC):
    @abstractmethod
    def get(self, **kwargs) -> list[SQLModel]:
        raise NotImplementedError


class FindOneMixin(AbstractBaseRepository, AbstractFindOneRepository):
    def find_one(self, **filters) -> SQLModel:
        with self.session as session:
            query = session.query(self.model)

            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

            return query.first()


class FindByIdMixin(AbstractFindByIdRepository, FindOneMixin):
    def find_by_id(self, record_id: Any) -> SQLModel:
        return self.find_one(id=record_id)


class GetMixin(AbstractBaseRepository, AbstractGetRepository):
    def get(self, **kwargs) -> list[SQLModel]:
        page_number = int(kwargs.get('page_number', 1)) - 1
        items_per_page = int(kwargs.get('items_per_page', 10))
        order = kwargs.get('order', [self.model.created_at.asc()])

        with self.session as session:
            return list(
                session.query(self.model).order_by(*order).offset(page_number * items_per_page).limit(items_per_page)
            )
