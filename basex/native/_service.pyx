__author__ = 'ziyan.yin'
__describe__ = ''

cimport cython
from cpython.list cimport PyList_Check, PyList_Size
from cpython.object cimport PyObject_HasAttrString, PyObject_GetAttrString, PyObject_GetAttr
from cpython.set cimport PySet_Contains
from cpython.dict cimport PyDict_Contains, PyDict_SetItem, PyDict_Items

cdef object _build_in = frozenset({'id','version','create_time','modify_time', 'deleted'})


cpdef void update(object model, bint ignore_none, object kwargs):
    cdef int res = 1
    for key, value in PyDict_Items(kwargs):
        if ignore_none and value is None:
            continue
        if PySet_Contains(_build_in, key):
            continue
        if PyDict_Contains(model.__dict__, key):
            res = PyDict_SetItem(model.__dict__, key, value)
        if res < 0:
            raise ValueError(key)


cpdef void update_batch(list models, bint ignore_none, object kwargs):
    for model in models:
        update(model, ignore_none, kwargs)



@cython.cdivision(True)
cpdef void paginate(object page, object columns, object stmt, long long total):
    cdef int size = page.size
    page.total = total
    page.pages = ((total - 1) / size) + 1

    if PyList_Check(page.orders) and PyList_Size(page.orders) > 0:
        stmt._order_by_clauses = [
            PyObject_GetAttr(columns, order.column) if order.asc else PyObject_GetAttr(columns, order.column).desc()
            for order in page.orders
        ]



cpdef object generic_model(object instance):
    cdef const char* orig_base = "__orig_bases__"
    cdef const char* args = "__args__"
    while PyObject_HasAttrString(instance, orig_base):
        instance = PyObject_GetAttrString(instance, orig_base)
    return PyObject_GetAttrString(instance[0], args)[0]
