__author__ = 'ziyan.yin'
__describe__ = 'base entity'

from typing import TypeVar, Generic, Optional, List, Union, Dict

from pydantic import BaseModel, BaseConfig
from pydantic.fields import ModelField
from pydantic.generics import GenericModel

from .enums import ResultEnum

Model = TypeVar('Model', bound=BaseModel)
InnerEntity = Union[BaseModel, str, int, float, bool, None]
Entity = TypeVar('Entity', bound=Union[InnerEntity, Dict[str, InnerEntity], List[InnerEntity]])


def default_json_encoder(x):
    return x


class BaseEntity(BaseModel):

    class Config(BaseConfig):
        json_encoders = {dict: default_json_encoder}


class OrderItem(BaseEntity):
    asc: bool = True
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
    __slots__ = ('code', 'message')

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


class ResultEntity(BaseEntity, GenericModel, Generic[Entity]):
    code: str = "00000"
    success: bool = True
    data: Optional[Entity] = None
    message: str = ""

    @classmethod
    def ok(cls, data: Optional[Entity] = None):
        return cls(data=data)

    @classmethod
    def error(cls, exc: BusinessError):
        return cls(code=exc.code, success=False, message=exc.message)


class DataTableEntity(BaseEntity):
    name: str
    header: List[str]
    data: List[tuple]
