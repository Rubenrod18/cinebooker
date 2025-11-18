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
    def find_one(self, **kwargs) -> SQLModel:
        options = kwargs.get('options')
        joins = kwargs.get('joins')
        filters = kwargs.get('filters')
        filter_by = kwargs.get('filter_by')

        with self.session as session:
            query = session.query(self.model)

            if options:
                query = query.options(*options)

            if joins:
                for join_model, join_type in joins:
                    if join_type == 'inner':
                        query = query.join(join_model)
                    elif join_type == 'outer':
                        query = query.outerjoin(join_model)

            if filters:
                query = query.filter(*filters)

            if filter_by:
                query = query.filter_by(**filter_by)

            return query.first()


class FindByIdMixin(AbstractFindByIdRepository, FindOneMixin):
    def find_by_id(self, record_id: Any) -> SQLModel:
        return self.find_one(filter_by={'id': record_id})


class GetMixin(AbstractBaseRepository, AbstractGetRepository):
    def get(self, **kwargs) -> list[SQLModel]:
        page_number = int(kwargs.get('page_number', 1)) - 1
        items_per_page = int(kwargs.get('items_per_page', 10))
        order = kwargs.get('order', [self.model.created_at.asc()])

        with self.session as session:
            return list(
                session.query(self.model).order_by(*order).offset(page_number * items_per_page).limit(items_per_page)
            )
