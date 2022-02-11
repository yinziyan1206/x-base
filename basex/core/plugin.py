__author__ = 'ziyan.yin'
__describe__ = ''


import polars
from sqlalchemy import text


class DataFrameMixin:

    def __init__(self):
        super().__init__()

    def _execute_query(self, stmt):
        raise NotImplementedError()

    async def query_dataframe(self, sql: str) -> polars.DataFrame:
        res = (await self._execute_query(lambda x: x.execute(text(sql)))).mappings()
        return polars.from_dicts([dict(x) for x in res.all()])
