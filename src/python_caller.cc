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
#include <boost/python/list.hpp>
#include <boost/python/stl_iterator.hpp>

#include "util/debug.hh"

namespace bp = boost::python;


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

#if BOOST_VERSION >= 103500
    _thrd->timed_join(boost::posix_time::milliseconds(3000));
#else
    // what if the thread doesn't terminate, due to a long-running python function?
    _thrd->join();
#endif
}


Patch::EventIterRange PythonCaller::call_now(Patch::Events & buf, Patch::EventIter it, bp::object const & fun)
{
    scoped_gil_lock gil;

    try {
        bp::object ret = fun(*it);

        if (ret.ptr() == Py_None) {
            // returned none
            it = buf.erase(it);
            return Patch::EventIterRange(it, it);
        }

        bp::extract<bp::list> e(ret);

        if (e.check()) {
            // returned python list
            it = buf.erase(it);

            if (bp::len(e())) {
                bp::stl_input_iterator<MidiEvent> begin(ret), end;

                Patch::EventIter first = buf.insert(it, *begin);
                buf.insert(it, ++begin, end);

                return Patch::EventIterRange(first, it);
            } else {
                return Patch::EventIterRange(it, it);
            }
        }

        bp::extract<bool> b(ret);

        if (b.check()) {
            // returned single event
            if (b) {
                Patch::EventIterRange r(it, it);
                r.advance_end(1);
                return r;
            } else {
                it = buf.erase(it);
                return Patch::EventIterRange(it, it);
            }
        }

        *it = bp::extract<MidiEvent>(ret);
        Patch::EventIterRange r(it, it);
        r.advance_end(1);
        return r;
    }
    catch (bp::error_already_set &) {
        PyErr_Print();
        it = buf.erase(it);
        return Patch::EventIterRange(it, it);
    }
}


void PythonCaller::call_deferred(bp::object const & fun, MidiEvent const & ev)
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
                (*c.fun)(bp::ptr(&c.ev));
            }
            catch (bp::error_already_set &) {
                PyErr_Print();
            }
        }
        else {
            boost::mutex::scoped_lock lock(mutex);
            _cond.wait(lock);
        }
    }
}
