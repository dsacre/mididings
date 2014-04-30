/*
 * mididings
 *
 * Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "config.hh"
#include "python_caller.hh"
#include "patch.hh"

#include <boost/version.hpp>
#include <boost/bind.hpp>

#include <boost/thread/mutex.hpp>

#include <boost/python/object.hpp>
#include <boost/python/ptr.hpp>
#include <boost/python/extract.hpp>
#include <boost/python/list.hpp>
#include <boost/python/stl_iterator.hpp>

#include "util/python.hh"
#include "util/debug.hh"

namespace bp = boost::python;


namespace mididings {


PythonCaller::PythonCaller(EngineCallback engine_callback)
  : _rb(new das::ringbuffer<AsyncCallInfo>(config::MAX_ASYNC_CALLS))
  , _engine_callback(engine_callback)
  , _quit(false)
{
    // start async thread
#if BOOST_VERSION >= 105000
    boost::thread::attributes attr;
    attr.set_stack_size(config::ASYNC_THREAD_STACK_SIZE);
    _thread.reset(new boost::thread(attr, boost::bind(&PythonCaller::async_thread, this)));
#else
    _thread.reset(new boost::thread(boost::bind(&PythonCaller::async_thread, this)));
#endif
}


PythonCaller::~PythonCaller()
{
    // release the GIL to ensure that we don't block the async thread
    das::python::scoped_gil_release release;

    _quit = true;
    _cond.notify_one();

    _thread->timed_join(boost::posix_time::milliseconds(config::ASYNC_JOIN_TIMEOUT));
}


template <typename B>
typename B::Range PythonCaller::call_now(B & buffer, typename B::Iterator it, bp::object const & fun)
{
    das::python::scoped_gil_lock gil;

    try
    {
        // call the python function
        bp::object ret = fun(*it);

        if (ret.ptr() == Py_None) {
            // returned None
            return Patch::delete_event(buffer, it);
        }

        bp::list ret_list = bp::extract<bp::list>(ret);
        bp::ssize_t len = bp::len(ret_list);

        if (len == 0) {
            return Patch::delete_event(buffer, it);
        }
        else if (len == 1) {
            *it = bp::extract<MidiEvent>(ret_list[0]);
            return Patch::keep_event(buffer, it);
        }
        else {
            bp::stl_input_iterator<MidiEvent> begin(ret_list), end;
            return Patch::replace_event(buffer, it, begin, end);
        }
    }
    catch (bp::error_already_set const &)
    {
        PyErr_Print();
        return Patch::delete_event(buffer, it);
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
        return Patch::keep_event(buffer, it);
    } else {
        return Patch::delete_event(buffer, it);
    }
}


void PythonCaller::async_thread()
{
    boost::mutex mutex;

    for (;;)
    {
        if (_rb->read_space()) {
            das::python::scoped_gil_lock gil;

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
        else if (_quit) {
            // program termination
            return;
        }
        else {
            // wait until woken up again
            boost::mutex::scoped_lock lock(mutex);
            _cond.timed_wait(lock, boost::posix_time::milliseconds(config::ASYNC_CALLBACK_INTERVAL));
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


} // mididings
