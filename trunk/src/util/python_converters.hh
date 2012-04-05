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

#include <boost/shared_ptr.hpp>

#include <algorithm>


namespace das {

namespace python_converters {


template <typename T>
struct vector_from_sequence_converter
  : from_python_converter<T, vector_from_sequence_converter<T> >
{
    static bool convertible(PyObject *obj) {
        return PySequence_Check(obj);
    }

    static void construct(T & vec, PyObject *obj) {
        Py_ssize_t size = PySequence_Size(obj);
        vec.reserve(size);

        for (Py_ssize_t i = 0; i != size; ++i) {
            PyObject *item = PySequence_GetItem(obj, i);
            vec.push_back(boost::python::extract<typename T::value_type>(item));
            boost::python::decref(item);
        }
    }
};


template <typename T>
struct vector_from_iterator_converter
  : from_python_converter<T, vector_from_iterator_converter<T> >
{
    static bool convertible(PyObject *obj) {
        return PyIter_Check(obj);
    }

    static void construct(T & vec, PyObject *obj) {
        PyObject *item;
        while ((item = PyIter_Next(obj))) {
            vec.push_back(boost::python::extract<typename T::value_type>(item));
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
  : boost::python::to_python_converter<T, vector_to_list_converter<T>
#ifdef BOOST_PYTHON_SUPPORTS_PY_SIGNATURES
        , true
#endif
    >
{
    static PyObject *convert(T const & vec) {
        boost::python::list ret;
        for (typename T::const_iterator it = vec.begin(); it != vec.end(); ++it) {
            ret.append(*it);
        }

        return boost::python::incref(ret.ptr());
    }

    static PyTypeObject const *get_pytype() {
        return &PyList_Type;
    }
};


template <typename T>
struct shared_ptr_vector_from_sequence_converter
  : from_python_converter<boost::shared_ptr<T const>, shared_ptr_vector_from_sequence_converter<T> >
{
    static bool convertible(PyObject *obj) {
        return PySequence_Check(obj);
    }

    static void construct(boost::shared_ptr<T const> & pvec, PyObject *obj) {
        Py_ssize_t size = PySequence_Size(obj);

        T *vec = new T(size);

        for (Py_ssize_t i = 0; i != size; ++i) {
            PyObject *item = PySequence_GetItem(obj, i);
            (*vec)[i] = boost::python::extract<typename T::value_type>(item);
            boost::python::decref(item);
        }

        pvec.reset(vec);
    }
};


template <typename T>
struct shared_ptr_vector_to_list_converter
  : boost::python::to_python_converter<boost::shared_ptr<T const>, shared_ptr_vector_to_list_converter<T>
#ifdef BOOST_PYTHON_SUPPORTS_PY_SIGNATURES
        , true
#endif
    >
{
    static PyObject *convert(boost::shared_ptr<T const> const & pvec) {
        boost::python::list ret;
        for (typename T::const_iterator it = pvec->begin(); it != pvec->end(); ++it) {
            ret.append(*it);
        }

        return boost::python::incref(ret.ptr());
    }

    static PyTypeObject const *get_pytype() {
        return &PyList_Type;
    }
};


#if PY_VERSION_HEX >= 0x02060000

template <typename T>
struct shared_ptr_vector_from_bytearray_converter
  : from_python_converter<boost::shared_ptr<T const>, shared_ptr_vector_from_bytearray_converter<T> >
{
    static bool convertible(PyObject *obj) {
        return PyByteArray_Check(obj);
    }

    static void construct(boost::shared_ptr<T const> & pvec, PyObject *obj) {
        char const *buffer = PyByteArray_AsString(obj);
        Py_ssize_t size = PyByteArray_Size(obj);

        T *vec = new T(size);

        std::copy(buffer, buffer + size, &vec->front());

        pvec.reset(vec);
    }
};


template <typename T>
struct shared_ptr_vector_to_bytearray_converter
  : boost::python::to_python_converter<boost::shared_ptr<T const>, shared_ptr_vector_to_bytearray_converter<T>
#ifdef BOOST_PYTHON_SUPPORTS_PY_SIGNATURES
        , true
#endif
    >
{
    static PyObject *convert(boost::shared_ptr<T const> const & pvec) {
        return PyByteArray_FromStringAndSize(reinterpret_cast<char const *>(&pvec->front()), pvec->size());
    }

    static PyTypeObject const *get_pytype() {
        return &PyByteArray_Type;
    }
};

#endif // PY_VERSION_HEX >= 0x02060000



template <typename T>
struct map_from_dict_converter
  : from_python_converter<T, map_from_dict_converter<T> >
{
    static bool convertible(PyObject *obj) {
        return PyDict_Check(obj);
    }

    static void construct(T & map, PyObject *obj) {
        PyObject *key_ptr, *value_ptr;
        Py_ssize_t pos = 0;

        while (PyDict_Next(obj, &pos, &key_ptr, &value_ptr)) {
            typename T::key_type key = boost::python::extract<typename T::key_type>(key_ptr);
            typename T::mapped_type value = boost::python::extract<typename T::mapped_type>(value_ptr);

            map[key] = value;
        }
    }
};


} // python_converters


template <typename T>
void register_vector_converters() {
    python_converters::vector_from_sequence_converter<T>();
    python_converters::vector_from_iterator_converter<T>();
    python_converters::vector_to_list_converter<T>();
}


template <typename T>
void register_shared_ptr_vector_converters() {
    python_converters::shared_ptr_vector_from_sequence_converter<T>();
    python_converters::shared_ptr_vector_to_list_converter<T>();
}

#if PY_VERSION_HEX >= 0x02060000
template <typename T>
void register_shared_ptr_vector_bytearray_converters() {
    python_converters::shared_ptr_vector_from_bytearray_converter<T>();
    python_converters::shared_ptr_vector_to_bytearray_converter<T>();
}
#endif // PY_VERSION_HEX >= 0x02060000

template <typename T>
void register_map_converters() {
    python_converters::map_from_dict_converter<T>();
}


} // namespace das


#endif // DAS_UTIL_PYTHON_CONVERTERS_HH
