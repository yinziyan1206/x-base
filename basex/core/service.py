__author__ = 'ziyan.yin'
__describe__ = 'base service'

import datetime
from typing import TypeVar, Generic, Optional, List, Callable

from sqlalchemy import func, text
from sqlalchemy.engine import Result, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Select


from .entity import Page
from ..db.mapper import SqlModel
from ..db.session import execute_statement, execute_query


Model = TypeVar('Model', bound=SqlModel)


class SessionService:

    @staticmethod
    async def _execute_query(query):
        return await execute_query(query)

    @staticmethod
    async def _execute_statement(stmt):
        return await execute_statement(stmt)

    async def query(self, sql: str) -> Result:
        res = await self._execute_query(lambda x: x.execute(text(sql)))
        return res

    async def select(self, stmt: Select) -> List[Row]:
        res = await self._execute_query(lambda x: x.execute(stmt.where(stmt.columns['deleted'] == 0)))
        return res.all()


class BaseService(Generic[Model], SessionService):
    root = None

    def __new__(cls, *args, **kwargs):
        if not cls.root:
            cls.root = super().__new__(cls, *args, **kwargs)
        return cls.root

    def __init__(self):
        self.stmt = select(self.model)
        super().__init__()

    async def get(self, index) -> Optional[Model]:
        if data := await self._execute_query(lambda x: x.get(self.model, index)):
            return data
        return None

    async def create(self, data: Model) -> Model:
        data.create_time = datetime.datetime.now()
        await self._execute_statement(lambda x: x.add(data))
        return data

    async def update(self, data: Model, ignore_none=True, **kwargs) -> Model:
        def _execute(x: AsyncSession):
            for k, v in kwargs.items():
                if k not in self.model.__table__.columns:
                    continue
                if k in ('id', 'version'):
                    continue
                if ignore_none and v is None:
                    continue
                setattr(data, k, v)
                x.add(data)
            data.modify_time = datetime.datetime.now()
            return data

        return await self._execute_statement(_execute)

    async def save(self, data: Model, ignore_none=True) -> Optional[Model]:
        if data.create_time:
            return await self.update(data, ignore_none=ignore_none, **data.dict())
        return await self.create(data)

    async def delete(self, data: Model, logic_delete=True) -> int:
        if logic_delete:
            await self.update(data, deleted=1)
            return 1
        res = await self._execute_statement(
            lambda x: x.delete(data)
        )
        return res.rowcount

    async def create_batch(self, *data: Model) -> List[Model]:
        for d in data:
            d.create_time = datetime.datetime.now()
        await self._execute_statement(lambda x: x.add_all(data))
        return list(data)

    async def update_batch(self, *data: Model, ignore_none=True, **kwargs) -> List[Model]:
        def _execute(x: AsyncSession):
            for k, v in kwargs.items():
                if k not in self.model.__table__.columns:
                    continue
                if k in ('id', 'version'):
                    continue
                if ignore_none and v is None:
                    continue
                for d in data:
                    setattr(d, k, v)
            x.add_all(data)
            return data

        return await self._execute_statement(_execute)

    async def select_list(self, fn: Callable[[Select], Select] = None) -> List[Model]:
        if fn is None:
            fn = self._init_fn
        res = await self._execute_query(lambda x: x.scalars(fn(self.stmt).where(self.model.deleted == 0)))
        return res.all()

    async def select_one(self, fn: Callable[[Select], Select] = None) -> Optional[Model]:
        if fn is None:
            fn = self._init_fn
        res = await self._execute_query(lambda x: x.scalars(fn(self.stmt).where(self.model.deleted == 0).limit(1)))
        return res.one_or_none()

    async def select_page(self, page: Page, fn: Callable[[Select], Select] = None) -> Page:
        if fn is None:
            fn = self._init_fn

        page.current = 1 if page.current < 1 else page.current
        page.size = 10 if page.size < 1 else page.size
        page.orders = [] if not page.orders else page.orders
        stmt = fn(self.stmt)

        async def _execute(session):
            nonlocal stmt

            res = await session.scalars(
                stmt.with_only_columns(func.count(self.model.id)).where(self.model.deleted == 0)
            )
            if item := res.first():
                page.total = item
                page.pages = int((page.total - 1) / page.size) + 1

            for order in page.orders:
                stmt = stmt.order_by(
                    getattr(self.model, order.column) if order.asc else getattr(self.model, order.column).desc()
                )

            stream = await session.stream_scalars(
                stmt.where(self.model.deleted == 0).limit(page.size).offset((page.current - 1) * page.size)
            )

            records = []
            async for data in stream:
                records.append(page.model.parse_obj(data))
            return records

        page.records = await self._execute_query(_execute)
        return page

    @property
    def model(self):
        temp = self.__class__
        while hasattr(temp, '__orig_bases__'):
            temp = getattr(temp, '__orig_bases__')[0]
        return temp.__args__[0]

    @staticmethod
    def _init_fn(select: Select) -> Select:
        return select
