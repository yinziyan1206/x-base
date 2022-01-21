__author__ = 'ziyan.yin'
__describe__ = 'flake sequence'

import datetime
import time
import socket

_last_point = 0
_last_sequence = 0
_sequence_length = 10

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    client.connect(('8.8.8.8', 80))
    _host_id = client.getsockname()[0]
finally:
    client.close()

_machine_id = (int(_host_id.split('.')[-1]) << 4)
_start_point = datetime.datetime(2020, 1, 1).timestamp()


def flake():
    global _last_sequence
    global _last_point

    point = int((time.time() - _start_point) * 100)
    if _last_point == point:
        count = _last_sequence + 1
        if count > (1 << _sequence_length):
            return 0
    else:
        count = 0
        _last_point = point
    _last_sequence = count
    return (_last_point << _sequence_length + 8) + (_machine_id << _sequence_length) + count
