/*
 * Copyright (C) 2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_TO_PYTHON_CONVERTER_HH
#define DAS_UTIL_TO_PYTHON_CONVERTER_HH

#include <Python.h>

#include <boost/python/to_python_converter.hpp>

#include <boost/utility/enable_if.hpp>

#include "util/is_shared_ptr.hh"


namespace das {
namespace python {


/**
 * Base class for converters from C++ to Python, supporting conversion from
 * both T and shared_ptr<T>.
 *
 * \tparam T    the data type to convert from.
 * \tparam P    the type to register a converter for, should be T
 *              or shared_ptr<T>.
 * \tparam C    the class that performs the conversion from a type T to
 *              a Python object.
 *
 * Class C must implement two static methods:
 * - PyObject *convert(T const &)
 * - PyTypeObject const *get_pytype()
 */
template <typename T, typename P, typename C>
struct to_python_converter
  : boost::python::to_python_converter<P, to_python_converter<T, P, C>
#ifdef BOOST_PYTHON_SUPPORTS_PY_SIGNATURES
        , true
#endif
    >
{
    template <typename U>
    static typename boost::disable_if<is_shared_ptr<U>, PyObject *>::type
    convert_tmpl(P const & t) {
        return C::convert(t);
    }

    template <typename U>
    static typename boost::enable_if<is_shared_ptr<U>, PyObject *>::type
    convert_tmpl(P const & t) {
        return C::convert(*t);
    }

    static PyObject *convert(P const & t) {
        return convert_tmpl<P>(t);
    }

    static PyTypeObject const *get_pytype() {
        return C::get_pytype();
    }
};


} // namespace python
} // namespace das


#endif // DAS_UTIL_TO_PYTHON_CONVERTER_HH
