/*
 * Copyright (C) 2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_PYTHON_CONVERTERS_HH
#define DAS_UTIL_PYTHON_CONVERTERS_HH

#include "util/from_python_converter.hh"

#include <boost/python/to_python_converter.hpp>
#include <boost/python/extract.hpp>
#include <boost/python/list.hpp>

#include <vector>
#include <map>


namespace das {

namespace python_converters {


template <typename T>
struct vector_from_sequence_converter
  : from_python_converter<std::vector<T>, vector_from_sequence_converter<T> >
{
    static bool convertible(PyObject *obj_ptr) {
        return PySequence_Check(obj_ptr);
    }

    static void construct(std::vector<T> & vec, PyObject *obj_ptr) {
        Py_ssize_t size = PySequence_Size(obj_ptr);
        vec.reserve(size);

        for (Py_ssize_t i = 0; i != size; ++i) {
            PyObject *item = PySequence_GetItem(obj_ptr, i);
            vec.push_back(boost::python::extract<T>(item));
            boost::python::decref(item);
        }
    }
};


template <typename T>
struct vector_from_iterator_converter
  : from_python_converter<std::vector<T>, vector_from_iterator_converter<T> >
{
    static bool convertible(PyObject *obj_ptr) {
        return PyIter_Check(obj_ptr);
    }

    static void construct(std::vector<T> & vec, PyObject *obj_ptr) {
        PyObject *item;
        while ((item = PyIter_Next(obj_ptr))) {
            vec.push_back(boost::python::extract<T>(item));
            boost::python::decref(item);
        }

        // propagate exceptions that occured inside a generator back to Python
        if (PyErr_Occurred()) {
            throw boost::python::error_already_set();
        }
    }
};


template <typename T>
struct vector_to_list_converter
  : boost::python::to_python_converter<std::vector<T>, vector_to_list_converter<T>
#ifdef BOOST_PYTHON_SUPPORTS_PY_SIGNATURES
        , true
#endif
    >
{
    static PyObject *convert(std::vector<T> const & vec) {
        boost::python::list ret;
        for (typename std::vector<T>::const_iterator it = vec.begin(); it != vec.end(); ++it) {
            ret.append(*it);
        }

        return boost::python::incref(ret.ptr());
    }

    static PyTypeObject const *get_pytype() {
        return &PyList_Type;
    }
};



template <typename K, typename V>
struct map_from_dict_converter
  : from_python_converter<std::map<K, V>, map_from_dict_converter<K, V> >
{
    static bool convertible(PyObject *obj_ptr) {
        return PyDict_Check(obj_ptr);
    }

    static void construct(std::map<K, V> & map, PyObject *obj_ptr) {
        PyObject *key_ptr, *value_ptr;
        Py_ssize_t pos = 0;

        while (PyDict_Next(obj_ptr, &pos, &key_ptr, &value_ptr)) {
            K key = boost::python::extract<K>(key_ptr);
            V value = boost::python::extract<V>(value_ptr);

            map[key] = value;
        }
    }
};


} // python_converters


template <typename T>
void register_vector_converters()
{
    python_converters::vector_from_sequence_converter<T>();
    python_converters::vector_from_iterator_converter<T>();
    python_converters::vector_to_list_converter<T>();
}


template <typename K, typename V>
void register_map_converters()
{
    python_converters::map_from_dict_converter<K, V>();
}


} // namespace das


#endif // DAS_UTIL_PYTHON_CONVERTERS_HH
