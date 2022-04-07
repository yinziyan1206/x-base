__author__ = 'ziyan.yin'
__describe__ = 'base model'

import datetime
import functools
from typing import Optional

import orjson
from sqlalchemy import Column, SmallInteger, BigInteger
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import SQLModel as _Model, Field

from ..core import entity
from ..native.cursor import next_val


@functools.lru_cache
def table_name_structure(name) -> str:
    output = []
    for i, c in enumerate(name.removesuffix('Model')):
        if c.isupper() and i > 0:
            output.append('_')
        output.append(c.lower())
    return ''.join(output)


class SqlModel(_Model, table=False):
    __bind_key__ = 'default'

    id: int = Field(
        default_factory=next_val,
        sa_column=Column(BigInteger(), primary_key=True, autoincrement=False)
    )
    deleted: int = Field(default=0, sa_column=Column(SmallInteger()))
    version: int = 0
    create_time: Optional[datetime.datetime]
    modify_time: Optional[datetime.datetime]

    @declared_attr
    def __mapper_args__(cls):
        return {
            "version_id_col": getattr(cls, '__table__').columns.version
        }

    @declared_attr  # type: ignore
    def __tablename__(cls):
        return table_name_structure(cls.__name__)

    class Config:
        orm_mode = True
        json_loads = orjson.loads
        json_dumps = entity.json_dumps_ex
