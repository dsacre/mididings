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
#include "backend/jack_realtime.hh"

#include <jack/jack.h>
#include <pthread.h>

#include "util/debug.hh"


namespace Mididings {
namespace Backend {


JACKRealtimeBackend::JACKRealtimeBackend(std::string const & client_name,
                                         PortNameVector const & in_port_names,
                                         PortNameVector const & out_port_names)
  : JACKBackend(client_name, in_port_names, out_port_names)
  , _out_rb(Config::MAX_JACK_EVENTS)
{
}


void JACKRealtimeBackend::start(InitFunction init, CycleFunction cycle)
{
    _run_init = init;
    _run_cycle = cycle;
}


int JACKRealtimeBackend::process(jack_nframes_t nframes)
{
    _nframes = nframes;

    clear_buffers(nframes);

    if (_run_init) {
        _run_init();
        _run_init.clear();  // RT-safe?
    }

    // write events from ringbuffer to JACK output buffers
    while (_out_rb.read_space()) {
        MidiEvent ev;
        _out_rb.read(ev);
        if (!write_event(ev, nframes)) {
            DEBUG_PRINT("couldn't write event from ringbuffer to output buffer");
        }
    }

    if (_run_cycle) {
        _run_cycle();
    }

    return 0;
}


bool JACKRealtimeBackend::input_event(MidiEvent & ev)
{
    return read_event(ev, _nframes);
}


void JACKRealtimeBackend::output_event(MidiEvent const & ev)
{
    if (pthread_self() == jack_client_thread_id(_client)) {
        // called within process(), write directly to output buffer
        if (!write_event(ev, _nframes)) {
            DEBUG_PRINT("couldn't write event to output buffer");
        }
    } else {
        // called elsewhere, write to ringbuffer
        if (!_out_rb.write(ev)) {
            DEBUG_PRINT("couldn't write event to output ringbuffer");
        }
    }
}


} // Backend
} // Mididings
