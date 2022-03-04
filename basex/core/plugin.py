__author__ = 'ziyan.yin'
__describe__ = ''

from typing import List

from sqlalchemy import func
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import TextClause

from basex.core.entity import Page, DataTableEntity
from basex.core.service import SessionService
from basex.db.mapper import SqlModel

try:
    import polars as dataframe
except ImportError:
    try:
        import pandas as dataframe
    except ImportError:
        dataframe = None


class DataFrameService(SessionService):

    async def query_dataframe(self, sql: TextClause, **kwargs) -> dataframe.DataFrame:
        res = (await self._execute_query(lambda x: x.execute(sql, kwargs))).mappings()
        return dataframe.from_dicts([dict(x) for x in res.all()])


class DataTableService(SessionService):

    async def parse_sql(self, sql: TextClause, **kwargs) -> DataTableEntity:
        result = await self.query(sql, **kwargs)
        columns = list(result.keys())
        if rows := result.all():
            return DataTableEntity(
                name="",
                header=columns,
                data=[tuple(row) for row in rows]
            )
        return DataTableEntity(name="", header=columns, data=[])

    async def parse_stmt(self, stmt: Select) -> DataTableEntity:
        if rows := await self.select(stmt):
            return DataTableEntity(
                name="",
                header=rows[0].keys(),
                data=[tuple(row) for row in rows]
            )
        return DataTableEntity(name="", header=[], data=[])

    def parse_obj(self, rows: List[SqlModel]) -> DataTableEntity:
        if not hasattr(self, 'model'):
            raise NotImplementedError
        columns = list(getattr(self, 'model').__fields__.keys())
        return DataTableEntity(name="", header=columns, data=[row.dict().values() for row in rows])

    @staticmethod
    def to_dicts(data: DataTableEntity) -> List[dict]:
        columns = data.header
        rows = data.data
        res = []
        for row in rows:
            res.append({key: value for key, value in zip(columns, row)})
        return res


class PageFilterService(SessionService):

    async def query_page(self, page: Page, stmt: Select) -> Page:
        page.current = 1 if page.current < 1 else page.current
        page.size = 10 if page.size < 1 else page.size
        page.orders = [] if not page.orders else page.orders

        async def _execute(session):
            count_stmt = stmt.with_only_columns(func.count())
            res = await session.scalars(
                count_stmt.where(count_stmt.exported_columns['deleted'] == 0)
            )
            if item := res.first():
                page.total = item
                page.pages = int((page.total - 1) / page.size) + 1

            stmt_order = stmt
            for order in page.orders:
                stmt_order = stmt_order.order_by(
                    stmt.exported_columns[order.column] if order.asc else stmt.exported_columns[order.column].desc()
                )

            stream = (await session.stream(
                stmt_order.where(
                    stmt.exported_columns["deleted"] == 0
                ).limit(page.size).offset((page.current - 1) * page.size)
            )).mappings()

            records = []
            async for data in stream:
                records.append(page.model.parse_obj(data))
            return records

        page.records = await self._execute_query(_execute)
        return page
