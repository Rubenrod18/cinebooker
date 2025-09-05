from abc import ABC, abstractmethod
from typing import Any

from sqlmodel import SQLModel

from app.repositories.core import AbstractBaseRepository


class AbstractBaseService(ABC):
    def __init__(self, repository: AbstractBaseRepository) -> None:
        self.repository = repository


class AbstractCreateService(ABC):
    @abstractmethod
    def create(self, **kwargs) -> SQLModel:
        raise NotImplementedError


class AbstractFindByIdService(ABC):
    @abstractmethod
    def find_by_id(self, record_id: Any) -> SQLModel:
        raise NotImplementedError


class AbstractGetService(ABC):
    @abstractmethod
    def get(self, **kwargs) -> list[SQLModel]:
        raise NotImplementedError


class FindByIdMixin(AbstractBaseService, AbstractFindByIdService):
    def find_by_id(self, record_id: Any) -> SQLModel | None:
        return self.repository.find_by_id(record_id)


class GetMixin(AbstractBaseService, AbstractGetService):
    def get(self, **kwargs) -> list[SQLModel]:
        return self.repository.get(**kwargs)
