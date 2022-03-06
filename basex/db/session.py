__author__ = 'ziyan.yin'
__describe__ = 'session'

from typing import Any, Type, Callable
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import settings

engine = None
create_session: Callable = lambda: None


def initial_engine():
    global engine
    global create_session
    engine = create_async_engine(
        **{k: v for k, v in settings.db.items() if k not in ('package', 'expire_on_commit')}
    )
    create_session = sessionmaker(
        engine,
        expire_on_commit=settings.db['expire_on_commit'] if 'expire_on_commit' in settings.db else False,
        class_=AsyncSession,
    )


async def execute_statement(func: Callable[[AsyncSession], Any]):
    async with create_session() as session:
        try:
            async with session.begin_nested():
                res = func(session)
                await session.commit()
                return res
        except Exception as ex:
            logger.exception(ex)
            await session.rollback()
            raise


async def execute_query(func: Callable[[AsyncSession], Any]):
    async with create_session() as session:
        try:
            res = await func(session)
            return res
        except Exception as ex:
            logger.exception(ex)
            raise


def transactional(rollback_for: Type[Exception] = Exception):
    def wrapper(func):
        async def inner(*args, **kwargs):
            async with create_session() as session:
                async with session.begin():
                    try:
                        res = await func(*args, **kwargs)
                    except Exception as ex:
                        logger.exception(ex)
                        if issubclass(ex.__class__, rollback_for):
                            await session.rollback()
                        else:
                            await session.commit()
                        raise
                    else:
                        await session.commit()
                        return res
        return inner

    return wrapper
