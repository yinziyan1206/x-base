__author__ = 'ziyan.yin'
__describe__ = 'core module'

import orjson

from .entity import BaseEntity
from ..config import settings

try:
    from starlette.requests import Request
    from fastapi import routing

    async def __request_body(self):
        if not hasattr(self, "_body"):
            self._body = b"".join([chunk async for chunk in self.stream()])
        return self._body

    async def __request_json(self):
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = orjson.loads(body)
        return self._json

    Request.body = __request_body  # type: ignore
    Request.json = __request_json  # type: ignore

    origin_serialize_response = routing.serialize_response

    async def __serialize_response(
            *,
            field=None,
            response_content,
            include=None,
            exclude=None,
            by_alias=True,
            exclude_unset=False,
            exclude_defaults=False,
            exclude_none=False,
            is_coroutine=True,
    ):
        if not settings.server.debug and isinstance(response_content, BaseEntity):
            return response_content.dict(
                by_alias=True,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )
        return await origin_serialize_response(
            field=field,
            response_content=response_content,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            is_coroutine=is_coroutine
        )

    routing.serialize_response = __serialize_response
except ImportError:  # pragma: nocover
    pass
