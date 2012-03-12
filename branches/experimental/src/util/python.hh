/*
 * Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_PYTHON_HH
#define DAS_UTIL_PYTHON_HH

#include <Python.h>

#include <boost/noncopyable.hpp>

namespace das {


class scoped_gil_lock
  : boost::noncopyable
{
  public:
    scoped_gil_lock() {
        _gil = PyGILState_Ensure();
    }

    ~scoped_gil_lock() {
        PyGILState_Release(_gil);
    }

  private:
    PyGILState_STATE _gil;
};


} // namespace das


#endif // DAS_UTIL_PYTHON_HH
