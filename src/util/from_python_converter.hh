/*
 * Copyright (C) 2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_FROM_PYTHON_CONVERTER_HH
#define DAS_UTIL_FROM_PYTHON_CONVERTER_HH

#include <Python.h>

#include <boost/python/converter/registry.hpp>

#include <boost/utility/enable_if.hpp>

#include "util/is_shared_ptr.hh"


namespace das {
namespace python {


/**
 * Base class for converters from Python to C++, supporting conversion to
 * both T and shared_ptr<T>.
 *
 * \tparam T    the data type to convert to, must be default-constructible.
 * \tparam P    the type to register a converter for, should be T
 *              or shared_ptr<T>.
 * \tparam C    the class that performs the conversion from a Python object
 *              to type T.
 *
 * Class C must implement two static methods:
 * - bool convertible(PyObject *)
 * - void construct(T &, PyObject *)
 */
template <typename T, typename P, typename C>
struct from_python_converter
{
    from_python_converter() {
        boost::python::converter::registry::push_back(
                    &convertible, &construct<P>, boost::python::type_id<P>());
    }

    static void *convertible(PyObject *obj) {
        if (!C::convertible(obj)) return 0;
        return obj;
    }

    template <typename U>
    static typename boost::disable_if<is_shared_ptr<U>, void>::type
    construct(PyObject *obj,
            boost::python::converter::rvalue_from_python_stage1_data *data) {
        void *storage = (reinterpret_cast<boost::python::converter::
                        rvalue_from_python_storage<T>*>(data))->storage.bytes;

        T *p = new (storage) T();

        C::construct(*p, obj);

        data->convertible = storage;
    }

    template <typename U>
    static typename boost::enable_if<is_shared_ptr<U>, void>::type
    construct(PyObject *obj,
            boost::python::converter::rvalue_from_python_stage1_data *data) {
        void *storage = (reinterpret_cast<boost::python::converter::
                        rvalue_from_python_storage<P>*>(data))->storage.bytes;

        T *p = new T();
        new (storage) P(p);

        C::construct(*p, obj);

        data->convertible = storage;
    }
};


} // namespace python
} // namespace das


#endif // DAS_UTIL_FROM_PYTHON_CONVERTER_HH
