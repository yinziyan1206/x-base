__author__ = 'ziyan.yin'
__describe__ = ''

from collections import Callable
from typing import Any, Awaitable, AsyncGenerator

cimport cython
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from ..db.session import session_factory


@cython.infer_types(True)
async def method_wrapper(func: Callable[[AsyncSession], Any], database: str = 'default') -> Any:
    async with session_factory(database) as session:
        if isinstance(session, AsyncSessionTransaction):
            cursor = session.session
        else:
            cursor = session
        try:
            res = func(cursor)
            await session.commit()
            return res
        except Exception as ex:
            logger.exception(ex)
            await session.rollback()
            raise


@cython.infer_types(True)
async def execute_wrapper(executable: Callable[[AsyncSession], Awaitable[Any]], database: str = 'default') -> Any:
    async with session_factory(database) as session:
        if isinstance(session, AsyncSessionTransaction):
            cursor = session.session
        else:
            cursor = session
        try:
            res = await executable(cursor)
            await session.commit()
            return res
        except Exception as ex:
            logger.exception(ex)
            await session.rollback()
            raise


@cython.infer_types(True)
async def stream_wrapper(stream: Callable[[AsyncSession], Any], database: str = 'default') -> AsyncGenerator:
    async with session_factory(database) as session:
        if isinstance(session, AsyncSessionTransaction):
            cursor = session.session
        else:
            cursor = session
        try:
            async for row in (await stream(cursor)):
                yield row
        except Exception as ex:
            logger.exception(ex)
            await session.rollback()
            raise
        else:
            await session.commit()


cpdef unicode get_binds(object model):
    return model.__bind_key__