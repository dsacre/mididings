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

#include <iostream>

#include <boost/foreach.hpp>

#include "util/string.hh"
#include "util/debug.hh"


namespace Mididings {
namespace Backend {


JACKBackend::JACKBackend(std::string const & client_name,
                         PortNameVector const & in_port_names,
                         PortNameVector const & out_port_names)
  : _current_frame(0)
{
    ASSERT(!client_name.empty());
    ASSERT(!in_port_names.empty());
    ASSERT(!out_port_names.empty());

    // create JACK client
    if ((_client = jack_client_open(client_name.c_str(), JackNullOption, NULL)) == 0) {
        throw Error("can't connect to jack server");
    }

    jack_set_process_callback(_client, &process_, static_cast<void*>(this));

    // create input ports
    BOOST_FOREACH (std::string const & port_name, in_port_names) {
        jack_port_t *p = jack_port_register(_client, port_name.c_str(), JACK_DEFAULT_MIDI_TYPE, JackPortIsInput, 0);
        if (p == NULL) {
            throw Error("error creating input port");
        }
        _in_ports.push_back(p);
    }

    // create output ports
    BOOST_FOREACH (std::string const & port_name, out_port_names) {
        jack_port_t *p = jack_port_register(_client, port_name.c_str(), JACK_DEFAULT_MIDI_TYPE, JackPortIsOutput, 0);
        if (p == NULL) {
            throw Error("error creating output port");
        }
        _out_ports.push_back(p);
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


void JACKBackend::connect_ports(PortConnectionMap const & in_port_connections,
                                PortConnectionMap const & out_port_connections)
{
    connect_ports_impl(in_port_connections, _in_ports, false);
    connect_ports_impl(out_port_connections, _out_ports, true);
}


void JACKBackend::connect_ports_impl(PortConnectionMap const & port_connections, std::vector<jack_port_t *> const & ports, bool out)
{
    if (port_connections.empty()) return;

    // get all JACK MIDI ports we could connect to
    char const **external_ports_array = jack_get_ports(_client, NULL, JACK_DEFAULT_MIDI_TYPE, out ? JackPortIsInput : JackPortIsOutput);
    if (!external_ports_array) return;

    // find end of array
    char const **end = external_ports_array;
    while (*end != NULL) ++end;

    // convert char* array to vector of strings
    PortNameVector external_ports(external_ports_array, end);

    jack_free(external_ports_array);

    // for each of our ports...
    BOOST_FOREACH (jack_port_t * port, ports) {
        std::string short_name = jack_port_short_name(port);
        std::string port_name = jack_port_name(port);

        PortConnectionMap::const_iterator element = port_connections.find(short_name);

        // break if no connections are defined for this port
        if (element == port_connections.end()) break;

        // for each regex pattern defined for this port...
        BOOST_FOREACH (std::string const & pattern, element->second) {
            // connect to all ports that match the pattern
            if (connect_matching_ports(port_name, pattern, external_ports, out) == 0) {
                std::cerr << "regular expression '" << pattern << "' didn't match any ports" << std::endl;
            }
        }
    }
}


int JACKBackend::connect_matching_ports(std::string const & port_name, std::string const & pattern, PortNameVector const & external_ports, bool out)
{
    try {
        // compile pattern into regex object
        das::regex regex(pattern, true);
        int count = 0;

        // for each external JACK MIDI port we might connect to...
        BOOST_FOREACH (std::string const & external_port, external_ports) {
            // check if port name matches regex
            if (regex.match(external_port)) {
                // connect output to input port
                std::string const & output_port = out ? port_name : external_port;
                std::string const & input_port = out ? external_port : port_name;

                int error = jack_connect(_client, output_port.c_str(), input_port.c_str());

                if (error && error != EEXIST) {
                    std::cerr << "could not connect " << output_port << " to " << input_port << std::endl;
                }

                ++count;
            }
        }
        return count;
    }
    catch (das::regex::compile_error & ex) {
        throw std::runtime_error(das::make_string() << "failed to parse regular expression '" << pattern << "': " << ex.what());
    }
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
