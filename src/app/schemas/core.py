from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, field_serializer

from app.utils.constants import DEFAULT_DATETIME_FORMAT


class IntegerPKMixin:
    id: int


class UUIDPKMixin:
    id: UUID


class CreatedUpdatedMixin:
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.strftime(DEFAULT_DATETIME_FORMAT)})

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime, _info):
        return value.strftime(DEFAULT_DATETIME_FORMAT) if value else None


class SoftDeleteMixin:
    deleted_at: datetime | None

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.strftime(DEFAULT_DATETIME_FORMAT)})

    @field_serializer('deleted_at')
    def serialize_datetime(self, value: datetime, _info):
        return value.strftime(DEFAULT_DATETIME_FORMAT) if value else None


class InactiveMixin:
    inactive_at: datetime | None

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.strftime(DEFAULT_DATETIME_FORMAT)})

    @field_serializer('inactive_at')
    def serialize_datetime(self, value: datetime, _info):
        return value.strftime(DEFAULT_DATETIME_FORMAT) if value else None
