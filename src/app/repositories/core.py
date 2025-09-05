from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from sqlmodel import Session, SQLModel


class AbstractBaseRepository(ABC):
    def __init__(self, model: SQLModel, session: Callable[..., AbstractContextManager[Session]]):
        self.model = model
        self.session = session


class AbstractCreateRepository(ABC):
    @abstractmethod
    def create(self, **kwargs) -> SQLModel:
        raise NotImplementedError


class AbstractFindByIdRepository(ABC):
    @abstractmethod
    def find_by_id(self, record_id) -> SQLModel | None:
        raise NotImplementedError


class AbstractGetRepository(ABC):
    @abstractmethod
    def get(self, **kwargs) -> list[SQLModel]:
        raise NotImplementedError


class FindByIdMixin(AbstractBaseRepository, AbstractFindByIdRepository):
    def find_by_id(self, record_id: Any) -> SQLModel:
        with self.session() as session:
            return session.query(self.model).filter(self.model.id == record_id).first()


class GetMixin(AbstractBaseRepository, AbstractGetRepository):
    def get(self, **kwargs) -> list[SQLModel]:
        page_number = int(kwargs.get('page_number', 1)) - 1
        items_per_page = int(kwargs.get('items_per_page', 10))
        order = kwargs.get('order', [self.model.created_at.asc()])

        with self.session() as session:
            return list(
                session.query(self.model).order_by(*order).offset(page_number * items_per_page).limit(items_per_page)
            )
