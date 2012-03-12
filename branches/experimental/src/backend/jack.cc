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
#include "backend/jack.hh"

#include <jack/jack.h>
#include <jack/midiport.h>

#include "util/debug.hh"


namespace Mididings {
namespace Backend {


JACKBackend::JACKBackend(std::string const & client_name,
                         std::vector<std::string> const & in_portnames,
                         std::vector<std::string> const & out_portnames)
  : _in_ports(in_portnames.size())
  , _out_ports(out_portnames.size())
  , _current_frame(0)
{
    ASSERT(!client_name.empty());
    ASSERT(!in_portnames.empty());
    ASSERT(!out_portnames.empty());

    // create JACK client
    if ((_client = jack_client_open(client_name.c_str(), JackNullOption, NULL)) == 0) {
        throw Error("can't connect to jack server");
    }

    jack_set_process_callback(_client, &process_, static_cast<void*>(this));

    // create input ports
    for (int n = 0; n < static_cast<int>(in_portnames.size()); n++) {
        _in_ports[n] = jack_port_register(_client, in_portnames[n].c_str(), JACK_DEFAULT_MIDI_TYPE, JackPortIsInput, 0);
        if (_in_ports[n] == NULL) {
            throw Error("error creating input port");
        }
    }

    // create output ports
    for (int n = 0; n < static_cast<int>(out_portnames.size()); n++) {
        _out_ports[n] = jack_port_register(_client, out_portnames[n].c_str(), JACK_DEFAULT_MIDI_TYPE, JackPortIsOutput, 0);
        if (_out_ports[n] == NULL) {
            throw Error("error creating output port");
        }
    }

    if (jack_activate(_client)) {
        throw Error("can't activate client");
    }
}


JACKBackend::~JACKBackend()
{
    jack_deactivate(_client);
    jack_client_close(_client);
}


int JACKBackend::process_(jack_nframes_t nframes, void *arg)
{
    JACKBackend *this_ = static_cast<JACKBackend*>(arg);

    this_->_input_port = 0;
    this_->_input_count = 0;

    int r = this_->process(nframes);

    this_->_current_frame += nframes;
    return r;
}


void JACKBackend::clear_buffers(jack_nframes_t nframes)
{
    for (int n = 0; n < static_cast<int>(_out_ports.size()); ++n) {
        void *port_buffer = jack_port_get_buffer(_out_ports[n], nframes);
        jack_midi_clear_buffer(port_buffer);
    }
}


bool JACKBackend::read_event(MidiEvent & ev, jack_nframes_t nframes)
{
    while (_input_port < static_cast<int>(_in_ports.size()))
    {
        void *port_buffer = jack_port_get_buffer(_in_ports[_input_port], nframes);
        int num_events = jack_midi_get_event_count(port_buffer);

        if (_input_count < num_events) {
            jack_midi_event_t jack_ev;
            VERIFY(!jack_midi_event_get(&jack_ev, port_buffer, _input_count));

            //std::cout << "in: " << jack_ev.time << std::endl;

            ev = buffer_to_midi_event(jack_ev.buffer, jack_ev.size, _input_port, _current_frame + jack_ev.time);

            if (++_input_count >= num_events) {
                ++_input_port;
                _input_count = 0;
            }

            return true;
        }

        ++_input_port;
    }

    return false;
}


bool JACKBackend::write_event(MidiEvent const & ev, jack_nframes_t nframes)
{
    unsigned char data[Config::MAX_JACK_EVENT_SIZE];
    std::size_t len = sizeof(data);
    int port;
    uint64_t frame;

    VERIFY(midi_event_to_buffer(ev, data, len, port, frame));

    if (!len) {
        return false;
    }

    void *port_buffer = jack_port_get_buffer(_out_ports[port], nframes);

    jack_nframes_t f;

    if (frame >= _current_frame) {
        // event received within current period, zero delay
        f = frame - _current_frame;
    } else if (frame >= _current_frame - nframes) {
        // event received during last period, exactly one period delay (minimize jitter)
        f = frame - _current_frame + nframes;
    } else {
        // event is older, send as soon as possible (minimize latency)
        f = 0;
    }

    //std::cout << "out: " << f << std::endl;
    if (!jack_midi_event_write(port_buffer, f, data, len)) {
        return true;
    } else {
        return false;
    }
}


} // Backend
} // Mididings
