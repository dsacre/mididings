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

#include "units.hh"
#include "midi_event.hh"

#include <boost/shared_ptr.hpp>

#include <boost/python/object.hpp>

#include <boost/thread/thread.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/condition.hpp>

#include <jack/ringbuffer.h>


class PythonCaller
{
  public:
    static const int MAX_ASYNC_CALLS = 64;

    PythonCaller();
    ~PythonCaller();

    bool call_now(boost::python::object & fun, MidiEvent & ev);
    void call_deferred(boost::python::object & fun, MidiEvent const & ev);

  private:
    void async_thread();

    struct AsyncCallInfo {
        boost::python::object const * fun;
        MidiEvent ev;
    };

    boost::shared_ptr<boost::thread> _thrd;

    jack_ringbuffer_t * _rb;
    boost::mutex        _rb_mutex;
    boost::condition    _rb_cond;
    volatile bool       _quit;

};


#endif // _PYTHON_CALL_HH
