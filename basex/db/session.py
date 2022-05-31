__author__ = 'ziyan.yin'
__describe__ = 'session'

from typing import Type, Dict, Union

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncSessionTransaction
from sqlalchemy.orm import sessionmaker, Session

from .mapper import SqlModel
from ..config import settings
from ..config.context import ContextWrapper
from ..native import logstash

engine: dict = {}
create_session: sessionmaker
transaction_group: Dict[str, ContextWrapper[AsyncSessionTransaction]] = {}


def initial_engine():
    global engine
    global create_session
    global transaction_group
    for tag, db in settings.datasource.items():
        transaction_group[tag] = ContextWrapper[AsyncSessionTransaction]('transaction')
        if tag != 'expire_on_commit':
            engine[tag] = create_async_engine(
                **{k: v for k, v in db.items() if k not in ('package', 'expire_on_commit')}
            )

    create_session = sessionmaker(
        expire_on_commit=settings.datasource.get('expire_on_commit', default=False),
        class_=AsyncSession,
        sync_session_class=RoutingSession,
    )
    logstash.intercept('sqlalchemy.engine.Engine')


def bind_database(database: str):

    def wrapper(model: SqlModel):
        model.__bind_key__ = database
        return model

    return wrapper


def session_factory(database: str = 'default') -> Union[AsyncSession, AsyncSessionTransaction]:
    database = database or 'default'
    session = transaction_group[database].value
    if session:
        return session
    else:
        return create_session()


def transactional(rollback_for: Type[Exception] = Exception):
    def wrapper(func):
        async def inner(self, *args, **kwargs):
            if not transaction_group[self.datasource].value:
                async with create_session() as session:
                    token = transaction_group[self.datasource].set(session.begin_nested())
                    try:
                        res = await func(self, *args, **kwargs)
                    except Exception as ex:
                        if issubclass(ex.__class__, rollback_for):
                            await session.rollback()
                        else:
                            await session.commit()
                        raise
                    else:
                        await session.commit()
                        return res
                    finally:
                        transaction_group[self.datasource].reset(token)
            else:
                return await func(self, *args, **kwargs)
        return inner

    return wrapper


class RoutingSession(Session):

    def get_bind(self, mapper=None, clause=None, **kw):
        if mapper and isinstance(mapper, SqlModel):
            return engine[mapper.__bind_key__].sync_engine
        return engine['default'].sync_engine
