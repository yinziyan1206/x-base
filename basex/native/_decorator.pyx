__author__ = 'ziyan.yin'
__describe__ = ''

from cpython.list cimport PyList_Append
from cpython.int cimport PyInt_Check
from cpython.unicode cimport PyUnicode_Split, PyUnicode_Join


cpdef str id_array_encoder(list arr):
    cdef object str_buf = []
    for num in arr:
        if not PyInt_Check(num):
            continue
        PyList_Append(str_buf, str(num))
    output = PyUnicode_Join(',', str_buf)
    return output


cpdef list id_array_decoder(object value):
    cdef list arr = PyUnicode_Split(value, ',', 128)
    output = [int(x) for x in arr]
    return output