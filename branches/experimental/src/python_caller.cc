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
#include "python_caller.hh"

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

#include "util/python.hh"
#include "util/debug.hh"

namespace bp = boost::python;


namespace Mididings {


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


template <typename B>
typename B::Range PythonCaller::call_now(B & buffer, typename B::Iterator it, bp::object const & fun)
{
    das::scoped_gil_lock gil;

    try
    {
        // call the python function
        bp::object ret = fun(*it);

        if (ret.ptr() == Py_None) {
            // returned None
            return delete_event(buffer, it);
        }

        bp::extract<bp::list> e(ret);

        if (e.check()) {
            // returned python list
            if (bp::len(e())) {
                bp::stl_input_iterator<MidiEvent> begin(ret), end;
                return replace_event(buffer, it, begin, end);
            } else {
                return delete_event(buffer, it);
            }
        }

        bp::extract<bool> b(ret);

        if (b.check()) {
            // returned bool
            if (b) {
                return keep_event(buffer, it);
            } else {
                return delete_event(buffer, it);
            }
        }

        // returned single event
        *it = bp::extract<MidiEvent>(ret);
        return keep_event(buffer, it);
    }
    catch (bp::error_already_set const &)
    {
        PyErr_Print();
        return delete_event(buffer, it);
    }
}


template <typename B>
typename B::Range PythonCaller::call_deferred(B & buffer, typename B::Iterator it, bp::object const & fun, bool keep)
{
    AsyncCallInfo c = { &fun, *it };

    // queue function/event, notify async thread
    VERIFY(_rb->write(c));
    _cond.notify_one();

    if (keep) {
        return keep_event(buffer, it);
    } else {
        return delete_event(buffer, it);
    }
}


template <typename B, typename IterT>
inline typename B::Range PythonCaller::replace_event(B & buffer, typename B::Iterator it, IterT begin, IterT end)
{
    it = buffer.erase(it);

    typename B::Iterator first = buffer.insert(it, *begin);
    buffer.insert(it, ++begin, end);

    return typename B::Range(first, it);
}


template <typename B>
inline typename B::Range PythonCaller::keep_event(B & /*buffer*/, typename B::Iterator it)
{
    typename B::Range r(it, it);
    r.advance_end(1);
    return r;
}


template <typename B>
inline typename B::Range PythonCaller::delete_event(B & buffer, typename B::Iterator it)
{
    it = buffer.erase(it);
    return typename B::Range(it, it);
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
            das::scoped_gil_lock gil;

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



// force template instantiations
template Patch::EventBufferRT::Range PythonCaller::call_now
            (Patch::EventBufferRT &, Patch::EventBufferRT::Iterator, boost::python::object const &);
template Patch::EventBuffer::Range PythonCaller::call_now
            (Patch::EventBuffer &, Patch::EventBuffer::Iterator, boost::python::object const &);
template Patch::EventBufferRT::Range PythonCaller::call_deferred
            (Patch::EventBufferRT &, Patch::EventBufferRT::Iterator, boost::python::object const &, bool);
template Patch::EventBuffer::Range PythonCaller::call_deferred
            (Patch::EventBuffer &, Patch::EventBuffer::Iterator, boost::python::object const &, bool);


} // Mididings
