__author__ = 'ziyan.yin'
__describe__ = 'background tasks'

import asyncio
import functools
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor
from typing import Awaitable, Callable

import anyio

worker_count: int = max(cpu_count(), 4)
executor = None


def create_process_workers():
    global executor
    executor = ProcessPoolExecutor(max_workers=worker_count)


async def call_subprocess(func, *args, **kwargs) -> Awaitable:
    """
    use multiprocess to execute function for event loop

    :param func: a callable
    :param args: positional arguments for the callable
    :param kwargs: keyword arguments for the callable
    :return: an awaitable that yields the return value of the function.
    """
    if not executor:
        create_process_workers()
    loop = asyncio.get_running_loop()
    task = functools.partial(func, **kwargs)
    return await loop.run_in_executor(executor, task, *args)


async def call_async(func, *args, **kwargs) -> Awaitable:
    """
    use threads to execute function for event loop

    :param func: a callable
    :param args: positional arguments for the callable
    :param kwargs: keyword arguments for the callable
    :return: an awaitable that yields the return value of the function.
    """
    task = functools.partial(func, **kwargs)
    return anyio.to_thread.run_sync(task, *args)


def run_in_thread(func) -> Callable:
    """
    async runner injection for event loop

    :param func: a callable
    :return: wrapped callable
    """
    def wrapper(*args, **kwargs) -> Awaitable:
        task = functools.partial(func, **kwargs)
        return anyio.to_thread.run_sync(task, *args)
    return wrapper
