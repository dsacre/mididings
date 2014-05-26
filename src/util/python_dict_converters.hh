/*
 * Copyright (C) 2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_PYTHON_DICT_CONVERTERS_HH
#define DAS_UTIL_PYTHON_DICT_CONVERTERS_HH

#include "util/from_python_converter.hh"
#include "util/to_python_converter.hh"

#include <boost/python/extract.hpp>


namespace das {
namespace python {


/**
 * Converter from a Python dictionary to std::map.
 */
template <typename T, typename P=T>
struct from_dict_converter
  : from_python_converter<T, P, from_dict_converter<T, P> >
{
    static bool convertible(PyObject *obj) {
        return PyDict_Check(obj);
    }

    static void construct(T & map, PyObject *obj) {
        PyObject *key_ptr, *value_ptr;
        Py_ssize_t pos = 0;

        while (PyDict_Next(obj, &pos, &key_ptr, &value_ptr)) {
            typename T::key_type key =
                    boost::python::extract<typename T::key_type>(key_ptr);
            typename T::mapped_type value =
                    boost::python::extract<typename T::mapped_type>(value_ptr);

            map[key] = value;
        }
    }
};


} // namespace python
} // namespace das


#endif // DAS_UTIL_PYTHON_DICT_CONVERTERS_HH
