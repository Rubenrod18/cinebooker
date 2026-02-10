import enum

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'


class BaseEnum(enum.StrEnum):
    @classmethod
    def to_list(cls, get_values=True):
        attr = 'name'
        if get_values:
            attr = 'value'
        return [getattr(_, attr) for _ in list(cls)]
