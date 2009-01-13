/*
 * mididings
 *
 * Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "config.hh"
#include "python_caller.hh"
#include "python_util.hh"

#include <boost/bind.hpp>

#include <boost/thread/mutex.hpp>
#if BOOST_VERSION < 103500
#  include <boost/thread/xtime.hpp>
#endif

#include <boost/python/object.hpp>
#include <boost/python/ptr.hpp>
#include <boost/python/extract.hpp>
#include <boost/python/list.hpp>
#include <boost/python/stl_iterator.hpp>

#include "util/debug.hh"

namespace bp = boost::python;


PythonCaller::PythonCaller(EngineCallback engine_callback)
  : _rb(new das::ringbuffer<AsyncCallInfo>(Config::MAX_ASYNC_CALLS))
  , _engine_callback(engine_callback)
  , _quit(false)
{
    // start async thread
    _thrd.reset(new boost::thread(boost::bind(&PythonCaller::async_thread, this)));
}


PythonCaller::~PythonCaller()
{
    _quit = true;
    _cond.notify_one();

#if BOOST_VERSION >= 103500
    _thrd->timed_join(boost::posix_time::milliseconds(Config::ASYNC_JOIN_TIMEOUT));
#else
    // what if the thread doesn't terminate, due to a long-running python function?
    _thrd->join();
#endif
}


PythonCaller::EventRange PythonCaller::call_now(Events & buf, EventIter it, bp::object const & fun)
{
    scoped_gil_lock gil;

    try
    {
        // call the python function
        bp::object ret = fun(*it);

        if (ret.ptr() == Py_None) {
            // returned none
            return delete_event(buf, it);
        }

        bp::extract<bp::list> e(ret);

        if (e.check()) {
            // returned python list
            if (bp::len(e())) {
                bp::stl_input_iterator<MidiEvent> begin(ret), end;
                return replace_event(buf, it, begin, end);
            } else {
                return delete_event(buf, it);
            }
        }

        bp::extract<bool> b(ret);

        if (b.check()) {
            // returned bool
            if (b) {
                return keep_event(buf, it);
            } else {
                return delete_event(buf, it);
            }
        }

        // returned single event
        *it = bp::extract<MidiEvent>(ret);
        return keep_event(buf, it);
    }
    catch (bp::error_already_set &)
    {
        PyErr_Print();
        return delete_event(buf, it);
    }
}


PythonCaller::EventRange PythonCaller::call_deferred(Events & buf, EventIter it, bp::object const & fun, bool keep)
{
    AsyncCallInfo c = { &fun, *it };

    // queue function/event, notify async thread
    VERIFY(_rb->write(c));
    _cond.notify_one();

    if (keep) {
        return keep_event(buf, it);
    } else {
        return delete_event(buf, it);
    }
}


template <typename IterT>
inline PythonCaller::EventRange PythonCaller::replace_event(Events & buf, EventIter it, IterT begin, IterT end)
{
    it = buf.erase(it);

    EventIter first = buf.insert(it, *begin);
    buf.insert(it, ++begin, end);

    return EventRange(first, it);
}


inline PythonCaller::EventRange PythonCaller::keep_event(Events & /*buf*/, EventIter it)
{
    EventRange r(it, it);
    r.advance_end(1);
    return r;
}


inline PythonCaller::EventRange PythonCaller::delete_event(Events & buf, EventIter it)
{
    it = buf.erase(it);
    return EventRange(it, it);
}


void PythonCaller::async_thread()
{
    boost::mutex mutex;

    for (;;)
    {
        // check for program termination
        if (_quit) {
            return;
        }

        if (_rb->read_space()) {
            scoped_gil_lock gil;

            // read event from ringbuffer
            AsyncCallInfo c;
            _rb->read(c);

            try {
                // call python function
                (*c.fun)(bp::ptr(&c.ev));
            }
            catch (bp::error_already_set &) {
                PyErr_Print();
            }
        }
        else {
            // wait until woken up again
            boost::mutex::scoped_lock lock(mutex);

#if BOOST_VERSION >= 103500
            _cond.timed_wait(lock, boost::posix_time::milliseconds(Config::ASYNC_CALLBACK_INTERVAL));
#else
            boost::xtime xt;
            boost::xtime_get(&xt, boost::TIME_UTC);
            xt.nsec += Config::ASYNC_CALLBACK_INTERVAL * 1000000;
            _cond.timed_wait(lock, xt);
#endif
        }

        _engine_callback();
    }
}
