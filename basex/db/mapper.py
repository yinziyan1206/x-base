__author__ = 'ziyan.yin'
__describe__ = 'base model'

import datetime
from typing import Optional

from sqlalchemy import Column, SmallInteger, BigInteger
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import SQLModel as _Model, Field

from ..native.cursor import Cursor


def get_table_name(name) -> str:
    table_name = []
    for c in name.removesuffix('Model'):
        if c.isupper():
            table_name.append('_')
        table_name.append(c.lower())
    table_name[0] = ''
    return ''.join(table_name)


class SqlModel(_Model, table=False):
    __bind_key__ = 'default'
    id: int = Field(
        default_factory=lambda: 0,
        sa_column=Column(BigInteger(), primary_key=True, autoincrement=False)
    )
    deleted: int = Field(default=0, sa_column=Column(SmallInteger()))
    version: int = 0
    create_time: Optional[datetime.datetime]
    modify_time: Optional[datetime.datetime]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__tablename__ = get_table_name(cls.__name__)
        cls.__fields__['id'].default_factory = Cursor().next_val

    @declared_attr
    def __mapper_args__(cls) -> dict:
        return {
            "version_id_col": getattr(cls, '__table__').columns.version
        }

    class Config:
        orm_mode = True
