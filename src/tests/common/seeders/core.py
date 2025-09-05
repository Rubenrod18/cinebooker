from abc import ABC

from app.repositories.core import AbstractBaseRepository
from tests.common.factories.base_factory import BaseFactory
from tests.common.seeders import seed_actions


class BaseSeeder(ABC):
    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority

    @seed_actions
    def seed(self, *args, **kwargs):
        raise NotImplementedError


class FactorySeeder(BaseSeeder):
    def __init__(self, name: str, priority: int, factory: type[BaseFactory]):
        super().__init__(name, priority)
        self.factory = factory


class RepositorySeeder:
    """

    NOTE: Instead of both FactorySeeder and RepositorySeeder inheriting BaseSeeder, make RepositorySeeder a mixin that
    adds the repository attribute. This change avoid Python’s MRO (Method Resolution Order) will try to call BaseSeeder
    twice (once for FactorySeeder and once for RepositorySeeder) if RepositorySeeder inherits BaseSeeder.

    """

    def __init__(self, repository: type[AbstractBaseRepository]):
        self.repository = repository
