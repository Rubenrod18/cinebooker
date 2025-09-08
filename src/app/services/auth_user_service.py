from sqlmodel import Session

from app.models import AuthUser
from app.repositories.auth_user_repository import AuthUserRepository
from app.services import core


class AuthUserService(
    core.AbstractBaseService,
    core.AbstractCreateService,
):
    def __init__(
        self,
        session: type[Session] = None,
        auth_user_repository: AuthUserRepository | None = None,
    ):
        super().__init__(repository=auth_user_repository or AuthUserRepository(session))

    def create(self, **kwargs) -> AuthUser:
        return self.repository.create(**kwargs)
