__author__ = 'ziyan.yin'
__describe__ = ''

import logging
from types import FrameType

cimport cython
from loguru import logger


class LoggerHandler(logging.Handler):

    def emit(self, record: logging.LogRecord) -> None:
        handle(record)


cdef void handle(object record):
    # Find caller from where originated the logged message
    frame: FrameType = logging.currentframe()
    cdef int depth = 2
    cdef unicode file_name = logging.__file__
    while frame.f_code.co_filename == file_name:
        frame = frame.f_back
        depth += 1

    logger.opt(depth=depth, exception=record.exc_info).log(record.levelname, record.getMessage())


@cython.infer_types(True)
def intercept(module: str = None):
    logging.getLogger(module).handlers = [LoggerHandler()]
