__author__ = 'ziyan.yin'
__describe__ = 'flake sequence'

import datetime
import time
import os

cimport cython

cdef int _sequence_length = 8
cdef int _machine_id = (os.getpid() % 0x100)
cdef double _start_point = datetime.datetime(2020, 1, 1).timestamp()


cdef class Cursor:
    cdef int cursor
    cdef long long last_point

    def __init__(self):
        self.cursor = 0
        self.last_point = 0

    cdef inline long long fetch(self):
        cdef long long count = 0
        cdef long long point = int((time.time() - _start_point) * 10)

        if self.last_point == point:
            count = self.cursor + 1
            if count > (1 << _sequence_length):
                return 0
        else:
            self.last_point = point
        self.cursor = count
        return (self.last_point << (_sequence_length + 8)) + (_machine_id << _sequence_length) + count

    @cython.infer_types(True)
    def next_val(self) -> int:
        index = self.fetch()
        while index == 0:
            index = self.fetch()
        return index
