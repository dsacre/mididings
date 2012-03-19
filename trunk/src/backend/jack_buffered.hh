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

#ifndef MIDIDINGS_BACKEND_JACK_BUFFERED_HH
#define MIDIDINGS_BACKEND_JACK_BUFFERED_HH

#include "backend/jack.hh"

#include <boost/scoped_ptr.hpp>

#include <boost/thread/thread.hpp>
#include <boost/thread/condition.hpp>
#include <boost/thread/mutex.hpp>

#include "util/ringbuffer.hh"


namespace Mididings {
namespace Backend {


/*
 * buffered JACK backend.
 * all events are written to a ringbuffer and processed in a separate thread.
 */
class JACKBufferedBackend
  : public JACKBackend
{
  public:
    JACKBufferedBackend(std::string const & client_name,
                        PortNameVector const & in_port_names,
                        PortNameVector const & out_port_names);

    virtual void start(InitFunction init, CycleFunction cycle);
    virtual void stop();

    virtual bool input_event(MidiEvent & ev);
    virtual void output_event(MidiEvent const & ev);

  private:
    virtual int process(jack_nframes_t);

    das::ringbuffer<MidiEvent> _in_rb;
    das::ringbuffer<MidiEvent> _out_rb;

    boost::scoped_ptr<boost::thread> _thread;

    boost::condition _cond;
    boost::mutex _mutex;

    volatile bool _quit;
};


} // Backend
} // Mididings


#endif // MIDIDINGS_BACKEND_JACK_BUFFERED_HH
