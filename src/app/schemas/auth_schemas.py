from datetime import datetime

from pydantic import BaseModel

from . import core


class AuthUserSchema(core.InactiveMixin, BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    date_joined: datetime
    last_login: datetime | None
