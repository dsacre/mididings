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


namespace Mididings {


class PythonCaller
  : boost::noncopyable
{
  public:

    typedef Patch::Events Events;
    typedef Patch::EventIter EventIter;
    typedef Patch::EventRange EventRange;

    typedef boost::function<void ()> EngineCallback;

    PythonCaller(EngineCallback engine_callback);
    ~PythonCaller();

    // calls python function immediately
    EventRange call_now(Events & buf, EventIter it, boost::python::object const & fun);
    // queues python function to be called asynchronously
    EventRange call_deferred(Events & buf, EventIter it, boost::python::object const & fun, bool keep);

  private:

    // replaces event with one or more events, returns the range containing the new events
    template <typename IterT>
    inline EventRange replace_event(Events & buf, EventIter it, IterT begin, IterT end);
    // leaves event unchanged, returns a range containing the single event
    inline EventRange keep_event(Events & buf, EventIter it);
    // removes event, returns empty range
    inline EventRange delete_event(Events & buf, EventIter it);


    void async_thread();

    struct AsyncCallInfo {
        boost::python::object const * fun;
        MidiEvent ev;
    };

    boost::scoped_ptr<das::ringbuffer<AsyncCallInfo> > _rb;

    boost::scoped_ptr<boost::thread> _thrd;

    EngineCallback _engine_callback;

    boost::condition _cond;
    volatile bool _quit;
};


} // Mididings


#endif // MIDIDINGS_PYTHON_CALLER_HH
