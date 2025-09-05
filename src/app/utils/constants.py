from enum import Enum

DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class BaseEnum(str, Enum):
    @classmethod
    def to_list(cls, get_values=True):
        attr = 'name'
        if get_values:
            attr = 'value'
        return [getattr(_, attr) for _ in list(cls)]
