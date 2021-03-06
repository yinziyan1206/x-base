__author__ = 'ziyan.yin'
__describe__ = 'type decorator'

from enum import Enum
from typing import List, Type

import orjson
from sqlalchemy import TypeDecorator, String, SmallInteger, JSON

from ..core.entity import BaseEntity
from ..native import _decorator


def get_value_error(origin, dest) -> ValueError:
    return ValueError(
        'expected %s value, got %s' % (origin, dest)
    )


class IntEnumDecorator(TypeDecorator):
    """
        Column type for storing Python enums in a database INTEGER column.

        This will behave erratically if a database value does not correspond to
        a known enum value.
    """
    impl = SmallInteger

    @property
    def python_type(self):
        return self.enum_type

    def __init__(self, enum_type=Enum):
        super().__init__()
        self.enum_type: Type[Enum] = enum_type

    def process_bind_param(self, value, dialect):
        if isinstance(value, self.enum_type):
            return value.value
        raise get_value_error(self.enum_type.__class__.__name__, value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_type(value)

    def copy(self, **kwargs):
        return IntEnumDecorator(self.enum_type)


class IdArrayDecorator(TypeDecorator):
    """
        Column type for storing Python List[int] in a database String column.
    """

    impl = String

    @property
    def python_type(self):
        return List

    def process_bind_param(self, value, dialect):
        if isinstance(value, List):
            if not value:
                return ''
            return _decorator.id_array_encoder(value)
        raise get_value_error('List[int]', value)

    def process_result_value(self, value, dialect):
        if not value:
            return []
        return _decorator.id_array_decoder(value)

    def copy(self, **kwargs):
        return IdArrayDecorator()


class JsonDecorator(TypeDecorator):
    """
        Column type for storing Python Dict in a database JSON column.
    """

    impl = JSON

    @property
    def python_type(self):
        return BaseEntity

    def __init__(self, model: Type[BaseEntity]):
        super().__init__()
        self.model: Type[BaseEntity] = model

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self.model):
            return orjson.dumps(value.dict()).decode()
        raise get_value_error(self.model.__name__, value.__name__)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.model.parse_obj(orjson.loads(value))

    def copy(self, **kwargs):
        return JsonDecorator(self.model)


class DictDecorator(TypeDecorator):
    """
        Column type for storing Python dict in a database Json column.
    """
    impl = JSON

    @property
    def python_type(self) -> type:
        return dict

    def process_bind_param(self, value, dialect) -> str:
        if isinstance(value, self.python_type):
            if not value:
                return '{}'
            return orjson.dumps(value).decode()
        raise get_value_error('dict', value)

    def process_result_value(self, value, dialect) -> dict:
        return orjson.loads(value)

    def copy(self):
        return DictDecorator()
