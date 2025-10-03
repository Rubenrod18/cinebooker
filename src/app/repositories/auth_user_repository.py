from sqlalchemy.orm import Session

from app.helpers.password_handler import PasswordHandler
from app.models import AuthUser
from app.repositories import core


class AuthUserRepository(
    core.AbstractBaseRepository,
    core.AbstractCreateRepository,
):
    def __init__(self, session: Session):
        super().__init__(model=AuthUser, session=session)

    def create(self, **kwargs) -> AuthUser:
        kwargs['password'] = PasswordHandler.ensure_password(kwargs.pop('password'))
        auth_user = self.model(**kwargs)
        self.session.add(auth_user)
        self.session.flush()
        return auth_user
