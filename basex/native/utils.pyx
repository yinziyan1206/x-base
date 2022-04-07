__author__ = 'ziyan.yin'
__describe__ = 'native utils interface'

from libc.string cimport strlen
from cpython.unicode cimport Py_UNICODE_ISUPPER, PyUnicode_AS_DATA, Py_UNICODE_ISLOWER


cpdef bint check_number(object context):
    if context is None:
        return False
    cdef int negative = 0
    cdef bint is_float = False
    cdef int n = len(context)
    if n < 1:
        return False
    if context[0] == '-':
        negative = 1
        if n < 2:
            return False
    for i in range(negative, n):
        arg = PyUnicode_AS_DATA(context[i])
        if strlen(arg) > 1:
            return False
        if i > negative and arg[0] == 46 and not is_float:
            is_float = True
            if i == n - 1:
                return False
            continue
        if arg[0] < 48 or arg[0] > 57:
            return False
    return True


cpdef bint check_chinese(char* args):
    cdef size_t n = strlen(args)
    cdef int i = 0
    cdef unsigned char* word_arr = b''
    while i < n:
        if args[i] & 0x80 == 0:
            i += 1
            continue
        if args[i] < -0x20:
            i += 2
            continue
        word_arr[0] = ((args[i] & 0x0f) << 4) | ((args[i + 1] & 0x3c) >> 2)
        word_arr[1] = ((args[i + 1] & 0x03) << 6) | (args[i + 2] & 0x3f)
        if 0x4e <= word_arr[0] <= 0x9f and word_arr[0] != 0x9f and word_arr[1] <= 0xa5:
            return True
        i += 3
    return False


cpdef bint check_letter(object context):
    if context is None:
        return True
    for ch in context:
        if not Py_UNICODE_ISLOWER(ch) and not Py_UNICODE_ISUPPER(ch):
            return False
    return True
