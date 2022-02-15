__author__ = 'ziyan.yin'
__describe__ = ''


import polars
from sqlalchemy import text, func
from sqlalchemy.sql import Select

from basex.core.entity import Page
from basex.core.service import SessionService


class DataFrameService(SessionService):

    def __init__(self):
        super().__init__()

    async def query_dataframe(self, sql: str) -> polars.DataFrame:
        res = (await self._execute_query(lambda x: x.execute(text(sql)))).mappings()
        return polars.from_dicts([dict(x) for x in res.all()])


class PageFilterService(SessionService):

    def __init__(self):
        super().__init__()

    async def query_page(self,  page: Page, stmt: Select) -> Page:
        page.current = 1 if page.current < 1 else page.current
        page.size = 10 if page.size < 1 else page.size
        page.orders = [] if not page.orders else page.orders

        async def _execute(session):
            count_stmt = stmt.with_only_columns(func.count())
            res = await session.scalars(
                count_stmt.where(count_stmt.columns["deleted"] == 0)
            )
            if item := res.first():
                page.total = item
                page.pages = int((page.total - 1) / page.size) + 1

            stmt_order = stmt
            for order in page.orders:
                stmt_order = stmt_order.order_by(
                    stmt.columns[order.column] if order.asc else stmt.columns[order.column].desc()
                )

            stream = (await session.stream(
                stmt_order.where(stmt.columns["deleted"] == 0).limit(page.size).offset((page.current - 1) * page.size)
            )).mappings()

            records = []
            async for data in stream:
                records.append(page.model.parse_obj(data))
            return records

        page.records = await self._execute_query(_execute)
        return page
