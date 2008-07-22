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

#include "python_caller.hh"
#include "util/debug.hh"

#include <boost/bind.hpp>

#include <boost/python/ptr.hpp>
#include <boost/python/extract.hpp>


PythonCaller::PythonCaller()
  : _quit(false)
{
    _rb = jack_ringbuffer_create(MAX_ASYNC_CALLS * sizeof(AsyncCallInfo));

    _thrd.reset(new boost::thread(boost::bind(&PythonCaller::async_thread, this)));
}


PythonCaller::~PythonCaller()
{
    _quit = true;
    _rb_cond.notify_one();
    // what if the thread doesn't terminate, due to a long-running python function?
    _thrd->join();

    jack_ringbuffer_free(_rb);
}


bool PythonCaller::call_now(boost::python::object & fun, MidiEvent & ev)
{
    PyGILState_STATE gil = PyGILState_Ensure();
    bool ret;

    try {
        boost::python::object obj = fun(boost::python::ptr(&ev));

        if (obj.ptr() == Py_None) {
            ret = true;
        } else {
            ret = boost::python::extract<bool>(obj);
        }
    } catch (boost::python::error_already_set &) {
        PyErr_Print();
        ret = false;
    }

    PyGILState_Release(gil);
    return ret;
}


void PythonCaller::call_deferred(boost::python::object & fun, MidiEvent const & ev)
{
    ASSERT(_rb);

    AsyncCallInfo c = { &fun, ev };

    if (jack_ringbuffer_write_space(_rb) >= sizeof(AsyncCallInfo)) {
        jack_ringbuffer_write(_rb, reinterpret_cast<char const *>(&c), sizeof(AsyncCallInfo));
        _rb_cond.notify_one();
    } else {
        FAIL();
    }
}


void PythonCaller::async_thread()
{
    boost::mutex mutex;

    for (;;) {
        if (_quit) {
            return;
        }

        if (jack_ringbuffer_read_space(_rb) >= sizeof(AsyncCallInfo)) {
            PyGILState_STATE gil = PyGILState_Ensure();

            AsyncCallInfo c;
            jack_ringbuffer_read(_rb, reinterpret_cast<char *>(&c), sizeof(AsyncCallInfo));

            try {
                (*c.fun)(boost::python::ptr(&c.ev));
            }
            catch (boost::python::error_already_set &) {
                PyErr_Print();
            }

            PyGILState_Release(gil);
        }
        else {
            boost::mutex::scoped_lock lock(mutex);
            _rb_cond.wait(lock);
        }
    }
}
