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

#ifndef MIDIDINGS_BACKEND_JACK_REALTIME_HH
#define MIDIDINGS_BACKEND_JACK_REALTIME_HH

#include "backend/jack.hh"

#include "util/ringbuffer.hh"


namespace Mididings {
namespace Backend {


/*
 * realtime JACK backend.
 * events are processed inside the JACK callback.
 */
class JACKRealtimeBackend
  : public JACKBackend
{
  public:
    JACKRealtimeBackend(std::string const & client_name,
                        PortNameVector const & in_port_names,
                        PortNameVector const & out_port_names);

    virtual void start(InitFunction init, CycleFunction cycle);
    virtual void stop() { }

    virtual bool input_event(MidiEvent & ev);
    virtual void output_event(MidiEvent const & ev);

  private:
    virtual int process(jack_nframes_t);

    InitFunction _run_init;
    CycleFunction _run_cycle;

    jack_nframes_t _nframes;

    das::ringbuffer<MidiEvent> _out_rb;
};


} // Backend
} // Mididings


#endif // MIDIDINGS_BACKEND_JACK_REALTIME_HH
