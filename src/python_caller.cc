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
#include "python_util.hh"

#include <boost/bind.hpp>

#include <boost/python/object.hpp>
#include <boost/python/ptr.hpp>
#include <boost/python/extract.hpp>

#include "util/debug.hh"


PythonCaller::PythonCaller()
  : _rb(new das::ringbuffer<AsyncCallInfo>(MAX_ASYNC_CALLS))
  , _quit(false)
{
    _thrd.reset(new boost::thread(boost::bind(&PythonCaller::async_thread, this)));
}


PythonCaller::~PythonCaller()
{
    _quit = true;
    _cond.notify_one();

    // what if the thread doesn't terminate, due to a long-running python function?
    _thrd->join();
}


bool PythonCaller::call_now(boost::python::object & fun, MidiEvent & ev)
{
    scoped_gil_lock gil;

    try {
        boost::python::object ret = fun(boost::python::ptr(&ev));

        if (ret.ptr() == Py_None) {
            return true;
        } else {
            return boost::python::extract<bool>(ret);
        }
    } catch (boost::python::error_already_set &) {
        PyErr_Print();
        return false;
    }
}


void PythonCaller::call_deferred(boost::python::object & fun, MidiEvent const & ev)
{
    AsyncCallInfo c = { &fun, ev };
    VERIFY(_rb->write(c));
    _cond.notify_one();
}


void PythonCaller::async_thread()
{
    boost::mutex mutex;

    for (;;) {
        if (_quit) {
            return;
        }

        if (_rb->read_space()) {
            scoped_gil_lock gil;

            AsyncCallInfo c;
            _rb->read(c);

            try {
                (*c.fun)(boost::python::ptr(&c.ev));
            }
            catch (boost::python::error_already_set &) {
                PyErr_Print();
            }
        }
        else {
            boost::mutex::scoped_lock lock(mutex);
            _cond.wait(lock);
        }
    }
}
