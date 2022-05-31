__author__ = 'ziyan.yin'
__describe__ = ''

from cpython.list cimport PyList_Append
from cpython.int cimport PyInt_Check
from cpython.unicode cimport PyUnicode_Split, PyUnicode_Join


cpdef str id_array_encoder(list arr):
    cdef list str_buf = []
    for num in arr:
        if not PyInt_Check(num):
            raise TypeError('id_array_encoder only accept int type')
        PyList_Append(str_buf, str(num))
    output = PyUnicode_Join(',', str_buf)
    return output


cpdef list id_array_decoder(object value):
    cdef list arr = PyUnicode_Split(value, ',', 128)
    return [int(i) for i in arr]
