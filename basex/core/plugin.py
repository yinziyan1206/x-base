__author__ = 'ziyan.yin'
__describe__ = ''

from typing import List

from sqlalchemy import func
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import TextClause

from ..core.entity import Page, DataTableEntity
from ..core.service import SessionService
from ..db.mapper import SqlModel
from ..native import _service

try:
    import polars as dataframe
except ImportError:
    try:
        import pandas as dataframe
    except ImportError:
        dataframe = None


class DataFrameService(SessionService):

    if dataframe:
        async def create_dataframe(self, sql: TextClause, **kwargs) -> dataframe.DataFrame:
            res = (await self.execute(sql, kwargs)).mappings()
            return dataframe.from_records([getattr(x, '_data') for x in res.all()], columns=list(res.keys()))


class DataTableService(SessionService):

    async def parse_sql(self, sql: TextClause, **kwargs) -> DataTableEntity:
        result = await self.execute(sql, **kwargs)
        columns = list(result.keys())
        if rows := result.all():
            return DataTableEntity(
                name="",
                header=columns,
                data=[getattr(row, '_data') for row in rows]
            )
        return DataTableEntity(name="", header=columns, data=[])

    async def parse_stmt(self, stmt: Select) -> DataTableEntity:
        if rows := (await self.execute(stmt)).mappings().all():
            return DataTableEntity(
                name="",
                header=rows[0].keys(),
                data=[getattr(row, '_data') for row in rows]
            )
        return DataTableEntity(name="", header=[], data=[])

    def parse_obj(self, rows: List[SqlModel]) -> DataTableEntity:
        if not hasattr(self, 'model'):
            raise NotImplementedError
        columns = list(getattr(self, 'model').__fields__.keys())
        return DataTableEntity(
            name="",
            header=columns,
            data=[tuple(map(lambda col, value=row: value.__dict__[col], columns)) for row in rows]
        )

    @staticmethod
    def to_dicts(data: DataTableEntity) -> List[dict]:
        columns = data.header
        rows = data.data
        res = []
        for row in rows:
            res.append({key: value for key, value in zip(columns, row)})
        return res


class PageFilterService(SessionService):

    async def paginate(self, page: Page, statement: Select) -> Page:
        page.current = page.current if page.current > 1 else 1
        page.size = page.size if 1 < page.size < 65536 else 10
        page.orders = page.orders or []

        count_stmt = statement.with_only_columns(func.count())
        stmt_order = statement
        page.records = []

        res = await self.scalars(
            count_stmt.where(count_stmt.exported_columns['deleted'] == 0)
        )

        if count := res.first():
            _service.paginate(page, statement.exported_columns, stmt_order, count)

            stream = self.stream_mappings(
                stmt_order.where(
                    statement.exported_columns["deleted"] == 0
                ).limit(page.size).offset((page.current - 1) * page.size)
            )
            async for data in stream:
                page.records.append(page.model.parse_obj(data))

        return page
