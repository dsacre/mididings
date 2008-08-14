/*
 * mididings
 *
 * Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _PYTHON_UTIL_HH
#define _PYTHON_UTIL_HH

#include <Python.h>

#include <boost/noncopyable.hpp>


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


#endif // _PYTHON_UTIL_HH
