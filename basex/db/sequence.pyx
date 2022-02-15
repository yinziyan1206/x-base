__author__ = 'ziyan.yin'
__describe__ = 'flake sequence'

import datetime
import time
import socket

import cython

cdef double _last_point = 0.0
cdef int _last_sequence = 0
cdef int _sequence_length = 10

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    client.connect(('8.8.8.8', 80))
    _host_id = client.getsockname()[0]
finally:
    client.close()

cdef int _machine_id = (int(_host_id.split('.')[-1]) << 4)
cdef double _start_point = datetime.datetime(2020, 1, 1).timestamp()


@cython.infer_types(True)
def flake():
    global _last_sequence
    global _last_point

    cdef double point = (time.time() - _start_point) * 100
    if int(_last_point) == int(point):
        count = _last_sequence + 1
        if count > (1 << _sequence_length):
            return 0
    else:
        count = 0
        _last_point = point
    _last_sequence = count
    return (int(_last_point) << (_sequence_length + 8)) + (_machine_id << _sequence_length) + count
