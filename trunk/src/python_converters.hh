/*
 * mididings
 *
 * Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "config.hh"

#include <boost/python/converter/registry.hpp>
#include <boost/python/to_python_converter.hpp>
#include <boost/python/extract.hpp>
#include <boost/python/list.hpp>

#include <vector>


namespace Mididings {


namespace {


template <typename T>
struct custom_vector_from_seq
{
    custom_vector_from_seq() {
        boost::python::converter::registry::push_back(&convertible, &construct, boost::python::type_id<std::vector<T> >());
    }

    static void *convertible(PyObject* obj_ptr) {
        if (!PySequence_Check(obj_ptr)) return 0;
        return obj_ptr;
    }

    static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data) {
        void *storage = ((boost::python::converter::rvalue_from_python_storage<std::vector<T> >*)(data))->storage.bytes;
        new (storage) std::vector<T>();

        std::vector<T> *v = (std::vector<T>*) storage;

        int l = PySequence_Size(obj_ptr);
        v->reserve(l);
        for (int i = 0; i != l; ++i) {
            PyObject *item = PySequence_GetItem(obj_ptr, i);
            v->push_back(boost::python::extract<T>(item));
            boost::python::decref(item);
        }
        data->convertible = storage;
    }
};


template <typename T>
struct custom_vector_from_iter
{
    custom_vector_from_iter() {
        boost::python::converter::registry::push_back(&convertible, &construct, boost::python::type_id<std::vector<T> >());
    }

    static void *convertible(PyObject* obj_ptr) {
        if (!PyIter_Check(obj_ptr) || PySequence_Check(obj_ptr)) return 0;
        return obj_ptr;
    }

    static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data) {
        void *storage = ((boost::python::converter::rvalue_from_python_storage<std::vector<T> >*)(data))->storage.bytes;
        new (storage) std::vector<T>();

        std::vector<T> *v = (std::vector<T>*) storage;

        PyObject *item;
        while ((item = PyIter_Next(obj_ptr))) {
            v->push_back(boost::python::extract<T>(item));
            boost::python::decref(item);
        }

        // propagate exceptions that occured inside a generator back to Python
        if (PyErr_Occurred()) {
            throw boost::python::error_already_set();
        }

        data->convertible = storage;
    }
};


template <typename T>
struct custom_vector_to_list
{
    static PyObject* convert(std::vector<T> const & v) {
        boost::python::list ret;
        for (typename std::vector<T>::const_iterator it = v.begin(); it != v.end(); ++it) {
            ret.append(*it);
        }

        return boost::python::incref(ret.ptr());
    }
};


} //


template <typename T>
void register_vector_converters()
{
    custom_vector_from_seq<T>();
    custom_vector_from_iter<T>();
    boost::python::to_python_converter<std::vector<T>, custom_vector_to_list<T> >();
}


} // Mididings
