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

#ifndef _PYTHON_CALL_HH
#define _PYTHON_CALL_HH

#include "midi_event.hh"
#include "patch.hh"

#include <boost/scoped_ptr.hpp>

#include <boost/python/object_fwd.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/condition.hpp>
#include <boost/noncopyable.hpp>

#include "util/ringbuffer.hh"


class PythonCaller
  : boost::noncopyable
{
  public:

    typedef Patch::Events Events;
    typedef Patch::EventIter EventIter;
    typedef Patch::EventRange EventRange;

    PythonCaller();
    ~PythonCaller();

    EventRange call_now(Events & buf, EventIter it, boost::python::object const & fun);
    EventRange call_deferred(Events & buf, EventIter it, boost::python::object const & fun, bool keep);

  private:

    template <typename IterT>
    inline EventRange replace_event(Events & buf, EventIter it, IterT begin, IterT end)
    {
        it = buf.erase(it);

        EventIter first = buf.insert(it, *begin);
        buf.insert(it, ++begin, end);

        return EventRange(first, it);
    }

    inline EventRange keep_event(Events & /*buf*/, EventIter it)
    {
        EventRange r(it, it);
        r.advance_end(1);
        return r;
    }

    inline EventRange delete_event(Events & buf, EventIter it)
    {
        it = buf.erase(it);
        return EventRange(it, it);
    }


    void async_thread();


    struct AsyncCallInfo {
        boost::python::object const * fun;
        MidiEvent ev;
    };

    boost::scoped_ptr<das::ringbuffer<AsyncCallInfo> > _rb;

    boost::scoped_ptr<boost::thread> _thrd;

    boost::condition _cond;
    volatile bool _quit;
};


#endif // _PYTHON_CALL_HH
