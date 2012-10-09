/*
 * Copyright (C) 2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_PYTHON_VECTOR_BYTEARRAY_CONVERTERS_HH
#define DAS_UTIL_PYTHON_VECTOR_BYTEARRAY_CONVERTERS_HH

#include "util/from_python_converter.hh"
#include "util/to_python_converter.hh"

#include <algorithm>
#include <iterator>


namespace das {
namespace python {


#if PY_VERSION_HEX >= 0x02060000

/**
 * Converter from a Python bytearray object to std::vector.
 */
template <typename T, typename P=T>
struct from_bytearray_converter
  : from_python_converter<T, P, from_bytearray_converter<T, P> >
{
    static bool convertible(PyObject *obj) {
        return PyByteArray_Check(obj);
    }

    static void construct(T & vec, PyObject *obj) {
        char const *buffer = PyByteArray_AsString(obj);
        Py_ssize_t size = PyByteArray_Size(obj);

        vec.reserve(size);
        std::copy(buffer, buffer + size, std::back_inserter(vec));
    }
};


/**
 * Converter from std::vector to a Python bytearray object.
 */
template <typename T, typename P=T>
struct to_bytearray_converter
  : to_python_converter<T, P, to_bytearray_converter<T, P> >
{
    static PyObject *convert(T const & vec) {
        return PyByteArray_FromStringAndSize(reinterpret_cast<char const *>(&vec.front()), vec.size());
    }

    static PyTypeObject const *get_pytype() {
        return &PyByteArray_Type;
    }
};

#endif // PY_VERSION_HEX >= 0x02060000


} // namespace python
} // namespace das


#endif // DAS_UTIL_PYTHON_VECTOR_BYTEARRAY_CONVERTERS_HH
