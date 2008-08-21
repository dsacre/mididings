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
#include "patch.hh" //////

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

    static int const MAX_ASYNC_CALLS = 256;

    PythonCaller();
    ~PythonCaller();

    Patch::EventIterRange call_now(Patch::Events & buf, Patch::EventIter it, boost::python::object const & fun);
    Patch::EventIterRange call_deferred(Patch::Events & buf, Patch::EventIter it, boost::python::object const & fun, bool keep);

  private:

    template <typename IterT>
    inline Patch::EventIterRange replace_event(Patch::Events & buf, Patch::EventIter it, IterT begin, IterT end)
    {
        it = buf.erase(it);

        Patch::EventIter first = buf.insert(it, *begin);
        buf.insert(it, ++begin, end);

        return Patch::EventIterRange(first, it);
    }

    inline Patch::EventIterRange keep_event(Patch::Events & /*buf*/, Patch::EventIter it)
    {
        Patch::EventIterRange r(it, it);
        r.advance_end(1);
        return r;
    }

    inline Patch::EventIterRange delete_event(Patch::Events & buf, Patch::EventIter it)
    {
        it = buf.erase(it);
        return Patch::EventIterRange(it, it);
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
