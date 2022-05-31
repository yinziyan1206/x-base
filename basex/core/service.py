__author__ = 'ziyan.yin'
__describe__ = 'base service'

import datetime
import functools
from typing import TypeVar, Generic, Optional, List, Callable, Any, Awaitable, AsyncGenerator

from sqlalchemy import func
from sqlalchemy.engine import Result, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Select, Selectable

from .entity import Page
from ..db.mapper import SqlModel
from ..native import _service, _session

Model = TypeVar('Model', bound=SqlModel)


class SessionService:
    __slots__ = ()

    async def _execute_wrapper(self, method: Callable[[AsyncSession], Awaitable[Any]]) -> Any:
        return await _session.execute_wrapper(method, self.datasource)

    async def _method_wrapper(self, method: Callable[[AsyncSession], Any]) -> Any:
        return await _session.method_wrapper(method, self.datasource)

    async def execute(self, statement, params=None, **kwargs) -> Result:
        statement = self.statement_intercept(statement)
        return await self._execute_wrapper(lambda x: x.execute(statement, params, **kwargs))

    async def scalar(self, statement, params=None, **kwargs) -> Any:
        statement = self.statement_intercept(statement)
        return await self._execute_wrapper(lambda x: x.scalar(statement, params, **kwargs))

    async def scalars(self, statement, params=None, **kwargs) -> ScalarResult:
        statement = self.statement_intercept(statement)
        return await self._execute_wrapper(lambda x: x.scalars(statement, params, **kwargs))

    def stream(self, statement, params=None, **kwargs) -> AsyncGenerator:
        statement = self.statement_intercept(statement)
        return _session.stream_wrapper(lambda x: x.stream(statement, params, **kwargs))

    def stream_mappings(self, statement, params=None, **kwargs) -> AsyncGenerator:
        statement = self.statement_intercept(statement)

        async def mappings(session):
            return (await session.stream(statement, params, **kwargs)).mappings()

        return _session.stream_wrapper(lambda x: mappings(x))

    def stream_scalars(self, statement, params=None, **kwargs) -> AsyncGenerator:
        statement = self.statement_intercept(statement)
        return _session.stream_wrapper(lambda x: x.stream_scalars(statement, params, **kwargs))

    @property
    def datasource(self) -> str:
        return 'default'

    @staticmethod
    def statement_intercept(statement: Selectable) -> Selectable:
        if isinstance(statement, Select) and 'deleted' in statement.exported_columns:
            return statement.where(statement.exported_columns['deleted'] == 0)
        return statement


class BaseService(Generic[Model], SessionService):
    root = None

    def __new__(cls, *args, **kwargs):
        if not cls.root:
            cls.root = super().__new__(cls, *args, **kwargs)
        return cls.root

    def __init__(self):
        super().__init__()

    async def get(self, index: int, options=None, **kw) -> Optional[Model]:
        if data := await self._execute_wrapper(lambda x: x.get(self.model, index, options, **kw)):
            return data
        return None

    async def save(self, data: Model, ignore_none: bool = True) -> Optional[Model]:
        if data.create_time:
            return await self.update(data, ignore_none=ignore_none, **data.dict())
        data.create_time = datetime.datetime.now()
        await _session.method_wrapper(lambda x: x.add(data), self.datasource)
        return data

    async def update(self, data: Model, ignore_none: bool = True, **kwargs) -> Model:
        def _execute(x: AsyncSession):
            _service.update(data, ignore_none, kwargs)
            data.modify_time = datetime.datetime.now()
            x.add(data)
            return data

        return await self._method_wrapper(_execute)

    async def delete(self, data: Model, logic_delete: bool = True) -> int:
        if logic_delete:
            def _logic_delete(x: AsyncSession):
                data.deleted = 1
                data.modify_time = datetime.datetime.now()
                x.add(data)
            await self._method_wrapper(_logic_delete)
        else:
            await self._execute_wrapper(lambda x: x.delete(data))
        return 1

    async def create_batch(self, *data: Model) -> List[Model]:
        for d in data:
            d.create_time = datetime.datetime.now()
        await self._method_wrapper(lambda x: x.add_all(data))
        return list(data)

    async def update_batch(self, *data: Model, ignore_none: bool = True, **kwargs) -> List[Model]:
        def _execute(x: AsyncSession):
            _service.update_batch(data, ignore_none, kwargs)
            current_time = datetime.datetime.now()
            for item in data:
                item.modify_time = current_time
            x.add_all(data)
            return data

        return await self._method_wrapper(_execute)

    async def paginate(self, page: Page, statement: Select = None) -> Page:
        if statement is None:
            statement = self.selectable()

        statement = self.statement_intercept(statement)
        page.current = page.current if page.current > 1 else 1
        page.size = page.size if 1 < page.size < 65536 else 10
        page.orders = page.orders or []
        page.records = []

        count_stmt = statement.with_only_columns(func.count(self.model.id))
        if count := await self.scalar(count_stmt):
            _service.paginate(page, self.model, statement, count)
            stream = self.stream_scalars(statement.limit(page.size).offset((page.current - 1) * page.size))
            async for data in stream:
                page.records.append(data)

        return page

    async def find(self, statement: Select = None) -> List[Model]:
        if statement is None:
            statement = self.selectable()
        res = await self.scalars(statement)
        return res.all()

    async def find_one(self, statement: Select = None) -> Optional[Model]:
        if statement is None:
            statement = self.selectable()
        res = await self.scalar(statement)
        return res

    def selectable(self) -> Select:
        return select(self.model)

    @property
    def model(self) -> Model:
        return _model(self.__class__)

    @property
    def datasource(self) -> str:
        return self.model.__bind_key__


@functools.lru_cache
def _model(service: type) -> Model:
    return _service.generic_model(service)
