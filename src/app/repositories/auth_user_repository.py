from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy.orm import Session

from app.helpers.password_handler import PasswordHandler
from app.models import AuthUser
from app.repositories import core


class AuthUserRepository(
    core.AbstractBaseRepository,
    core.AbstractCreateRepository,
):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        super().__init__(model=AuthUser, session=session)

    def create(self, **kwargs) -> AuthUser:
        auto_flush = kwargs.pop('auto_flush', True)
        kwargs['password'] = PasswordHandler.ensure_password(kwargs.pop('password'))
        auth_user = self.model(**kwargs)

        if auto_flush:
            self.session.add(auth_user)
            self.session.flush()

        return auth_user
