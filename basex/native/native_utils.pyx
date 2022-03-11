__author__ = 'ziyan.yin'
__describe__ = ''

from libc.string cimport strlen


cpdef bint check_blank(char* args):
    cdef size_t n = strlen(args)
    cdef int i = 0
    cdef int word = 0
    while i < n:
        if args[i] & 0x80 == 0:
            if (args[i] < 9 or args[i] > 15) and args[i] != 32:
                return False
            i += 1
            continue
        if args[i] < -32:
            word = ((args[i] & 0x03) << 6) | (args[i + 1] & 0x3F)
            if word != 160:
                return False
            i += 2
            continue
        word = (((args[i] & 0x0F) << 4) | ((args[i + 1] & 0x3C) >> 2)) << 8
        word += ((args[i + 1] & 0x03) << 6) | (args[i + 2] & 0x3F)
        if word != 8199 and word != 8239:
            return False
        i += 4
    return True


cpdef bint check_number(args):
    cdef int negative = 0
    cdef bint is_float = False
    cdef size_t n = strlen(args)
    if n < 1:
        return False
    if args[0] == 45:
        negative = 1
        if n < 2:
            return False
    for i in range(negative, n):
        if i > negative and args[i] == 46 and not is_float:
            is_float = True
            if i == n - 1:
                return False
            continue
        if args[i] < 48 or args[i] > 57:
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
        if args[i] < -32:
            i += 2
            continue
        word_arr[0] = ((args[i] & 0x0F) << 4) | ((args[i + 1] & 0x3C) >> 2)
        word_arr[1] = ((args[i + 1] & 0x03) << 6) | (args[i + 2] & 0x3F)
        if 0x4e <= word_arr[0] <= 0x9f and word_arr[0] != 0x9f and word_arr[1] <= 0xa5:
            return True
        i += 3
    return False


cpdef bint check_alpha(char* args):
    cdef size_t n = strlen(args)
    for i in range(n):
        if args[i] < 65 or 90 < args[i] < 97 or args[i] > 122:
            return False
    return True


cpdef bint check_letter(char* args):
    cdef size_t n = strlen(args)
    for i in range(n):
        if args[i] < 47 or 57 < args[i] < 65 or 90 < args[i] < 97 or args[i] > 122:
            return False
    return True


cpdef bint check_title(char* args):
    cdef size_t n = strlen(args)
    for i in range(n):
        if args[i] < 47 or 57 < args[i] < 65 or 65 < args[i] < 95 or args[i] == 96 or args[i] > 122:
            return False
    return True
