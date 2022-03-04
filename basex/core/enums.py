__author__ = 'ziyan.yin'
__describe__ = 'base entity'

from typing import TypeVar, Generic, Optional, List, Union, Any

import orjson
from pydantic import BaseModel, BaseConfig
from pydantic.fields import ModelField
from pydantic.generics import GenericModel

from .enums import ResultEnum


Model = TypeVar('Model', bound=Union[BaseModel, List[BaseModel]])


def default_json_encoder(x):
    return x


def json_dumps_ex(v, *, indent=None, default=None, sort_keys=False):
    option = orjson.OPT_UTC_Z | orjson.OPT_SERIALIZE_NUMPY
    if sort_keys:
        option |= orjson.OPT_SORT_KEYS
    if indent:
        option |= orjson.OPT_INDENT_2
    return orjson.dumps(v, default=default, option=option).decode()


class BaseEntity(BaseModel):
    __json_encoder__ = default_json_encoder

    class Config(BaseConfig):
        json_loads = orjson.loads
        json_dumps = json_dumps_ex


class OrderItem(BaseEntity):
    asc: bool
    column: str


class Page(BaseEntity, GenericModel, Generic[Model]):
    orders: Optional[List[OrderItem]]
    records: Optional[List[Model]]
    current: int = 0
    pages: int = 0
    total: int = 0
    size: int = 0

    @property
    def model(self):
        temp: ModelField = self.__class__.__fields__['records']
        return temp.type_


class BusinessError(Exception):
    __slots__ = ['code', 'message']

    def __init__(self, result: ResultEnum = None, code: str = "00000", message: str = ""):
        if result:
            self.code = result.value[0]
            self.message = message or result.value[1]
        else:
            self.code = code
            self.message = message
        super().__init__(self)

    def __str__(self):
        return '[%s]%s' % (self.code, self.message)

    def __repr__(self):
        return '[%s]%s' % (self.code, self.message)


class ResultEntity(BaseEntity, GenericModel, Generic[Model]):
    code: str = "00000"
    success: bool = True
    data: Optional[Model] = None
    message: str = ""

    @classmethod
    def ok(cls, data: Optional[Model] = None):
        return cls(data=data)

    @classmethod
    def error(cls, exc: BusinessError):
        return cls(code=exc.code, success=False, message=exc.message)


class DataTableEntity(BaseEntity):
    name: str
    header: List[str]
    data: List[tuple]
