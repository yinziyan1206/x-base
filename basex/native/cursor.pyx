__author__ = 'ziyan.yin'
__describe__ = 'flake sequence'

import datetime
import time
import os

cimport cython

cdef long long _last_point = 0
cdef int _last_sequence = 0
cdef int _sequence_length = 8
cdef int _machine_id = (os.getpid() % 0x100)
cdef double _start_point = datetime.datetime(2020, 1, 1).timestamp()


cdef long long fetch():
    global _last_sequence
    global _last_point

    cdef long long count = 0
    cdef long long point = int((time.time() - _start_point) * 10)

    if _last_point == point:
        count = _last_sequence + 1
        if count > (1 << _sequence_length):
            return 0
    else:
        _last_point = point
    _last_sequence = count
    return (_last_point << (_sequence_length + 8)) + (_machine_id << _sequence_length) + count


@cython.infer_types(True)
def next_val() -> int:
    index = fetch()
    while index == 0:
        index = fetch()
    return index