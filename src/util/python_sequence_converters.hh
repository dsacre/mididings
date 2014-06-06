/*
 * Copyright (C) 2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_PYTHON_SEQUENCE_CONVERTERS_HH
#define DAS_UTIL_PYTHON_SEQUENCE_CONVERTERS_HH

#include "util/from_python_converter.hh"
#include "util/to_python_converter.hh"

#include <boost/python/extract.hpp>
#include <boost/python/list.hpp>


namespace das {
namespace python {


/**
 * Converter from Python sequence or iterator to C++ container.
 */
template <typename T, typename P=T>
struct from_sequence_converter
  : from_python_converter<T, P, from_sequence_converter<T, P> >
{
    static bool convertible(PyObject *obj) {
        return PySequence_Check(obj) || PyIter_Check(obj);
    }

    static void construct(T & cont, PyObject *obj) {
        if (PySequence_Check(obj)) {
            Py_ssize_t size = PySequence_Size(obj);
            cont.reserve(size);

            for (Py_ssize_t i = 0; i != size; ++i) {
                PyObject *item = PySequence_GetItem(obj, i);
                cont.push_back(
                        boost::python::extract<typename T::value_type>(item));
                boost::python::decref(item);
            }
        }
        else {
            PyObject *item;
            while ((item = PyIter_Next(obj))) {
                cont.push_back(
                        boost::python::extract<typename T::value_type>(item));
                boost::python::decref(item);
            }

            // propagate exceptions that occured inside a generator back
            // to Python
            if (PyErr_Occurred()) {
                throw boost::python::error_already_set();
            }
        }
    }
};


/**
 * Converter from C++ container to Python list.
 */
template <typename T, typename P=T>
struct to_list_converter
  : to_python_converter<T, P, to_list_converter<T, P> >
{
    static PyObject *convert(T const & cont) {
        boost::python::list ret;
        for (typename T::const_iterator it = cont.begin();
                it != cont.end(); ++it) {
            ret.append(*it);
        }

        return boost::python::incref(ret.ptr());
    }

    static PyTypeObject const *get_pytype() {
        return &PyList_Type;
    }
};


} // namespace python
} // namespace das


#endif // DAS_UTIL_PYTHON_SEQUENCE_CONVERTERS_HH
