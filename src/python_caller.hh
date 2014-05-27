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

#ifndef MIDIDINGS_PYTHON_CALLER_HH
#define MIDIDINGS_PYTHON_CALLER_HH

#include "midi_event.hh"
#include "patch.hh"

#include <boost/scoped_ptr.hpp>
#include <boost/function.hpp>

#include <boost/python/object_fwd.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/condition.hpp>
#include <boost/noncopyable.hpp>

#include "util/ringbuffer.hh"


namespace mididings {


class PythonCaller
  : boost::noncopyable
{
  public:

    typedef boost::function<void()> EngineCallback;

    PythonCaller(EngineCallback engine_callback);
    ~PythonCaller();

    // call python function immediately
    template <typename B>
    typename B::Range call_now(B & buf, typename B::Iterator it,
                               boost::python::object const & fun);

    // queue python function to be called asynchronously
    template <typename B>
    typename B::Range call_deferred(B & buf, typename B::Iterator it,
                               boost::python::object const & fun, bool keep);

  private:

    void async_thread();

    struct AsyncCallInfo {
        boost::python::object const * fun;
        MidiEvent ev;
    };

    boost::scoped_ptr<das::ringbuffer<AsyncCallInfo> > _rb;

    boost::scoped_ptr<boost::thread> _thread;

    EngineCallback _engine_callback;

    boost::condition _cond;
    volatile bool _quit;
};


} // mididings


#endif // MIDIDINGS_PYTHON_CALLER_HH
