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


namespace das {


template <typename T, typename Conversion>
struct from_python_converter
{
    from_python_converter() {
        boost::python::converter::registry::push_back(&convertible, &construct, boost::python::type_id<T>());
    }

    static void *convertible(PyObject *obj) {
        if (!Conversion::convertible(obj)) return 0;
        return obj;
    }

    static void construct(PyObject *obj, boost::python::converter::rvalue_from_python_stage1_data *data) {
        void *storage = (reinterpret_cast<boost::python::converter::rvalue_from_python_storage<T>*>(data))->storage.bytes;

        new (storage) T();
        T & t = *(T *) storage;

        Conversion::construct(t, obj);

        data->convertible = storage;
    }
};


} // namespace das


#endif // DAS_UTIL_FROM_PYTHON_CONVERTER_HH
