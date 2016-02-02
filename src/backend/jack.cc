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

#include "config.hh"
#include "backend/jack.hh"

#include <jack/jack.h>
#include <jack/midiport.h>

#include <iostream>
#include <algorithm>

#include <boost/foreach.hpp>

#include "util/string.hh"
#include "util/debug.hh"


namespace mididings {
namespace backend {


JACKBackend::JACKBackend(std::string const & client_name,
                         PortNameVector const & in_port_names,
                         PortNameVector const & out_port_names)
  : _current_frame(0)
  , _input_queue(config::JACK_MAX_EVENTS)
  , _last_written_frame(out_port_names.size())
{
    ASSERT(!client_name.empty());

    // create JACK client
    _client = jack_client_open(client_name.c_str(), JackNoStartServer, NULL);
    if (_client == NULL) {
        throw Error("can't connect to jack server");
    }

    jack_set_process_callback(_client, &process_, static_cast<void*>(this));

    // create input ports
    BOOST_FOREACH (std::string const & port_name, in_port_names) {
        jack_port_t *p = jack_port_register(_client, port_name.c_str(),
                                            JACK_DEFAULT_MIDI_TYPE,
                                            JackPortIsInput, 0);
        if (p == NULL) {
            throw Error("error creating input port");
        }
        _in_ports.push_back(p);
    }

    // create output ports
    BOOST_FOREACH (std::string const & port_name, out_port_names) {
        jack_port_t *p = jack_port_register(_client, port_name.c_str(),
                                            JACK_DEFAULT_MIDI_TYPE,
                                            JackPortIsOutput, 0);
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


void JACKBackend::connect_ports(
        PortConnectionMap const & in_port_connections,
        PortConnectionMap const & out_port_connections)
{
    connect_ports_impl(in_port_connections, _in_ports, false);
    connect_ports_impl(out_port_connections, _out_ports, true);
}


std::string JACKBackend::get_actual_client_name()
{
    std::string client_name = jack_get_client_name(_client);
    return client_name;
}


std::string JACKBackend::get_client_uuid()
{
    std::string client_uuid = jack_get_uuid_for_client_name(_client, jack_get_client_name(_client));
    return client_uuid;
}


void JACKBackend::connect_ports_impl(
        PortConnectionMap const & port_connections,
        std::vector<jack_port_t *> const & ports,
        bool out)
{
    if (port_connections.empty()) return;

    // get all JACK MIDI ports we could connect to
    char const **external_ports_array = jack_get_ports(
                                _client, NULL, JACK_DEFAULT_MIDI_TYPE,
                                out ? JackPortIsInput : JackPortIsOutput);
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

        PortConnectionMap::const_iterator element =
                port_connections.find(short_name);

        // continue with next port if no connections are defined for this port
        if (element == port_connections.end()) continue;

        // for each regex pattern defined for this port...
        BOOST_FOREACH (std::string const & pattern, element->second) {
            // connect to all ports that match the pattern
            if (connect_matching_ports(port_name, pattern,
                                       external_ports, out) == 0) {
                std::cerr << "warning: regular expression '" << pattern
                          << "' didn't match any JACK MIDI ports" << std::endl;
            }
        }
    }
}


int JACKBackend::connect_matching_ports(
        std::string const & port_name,
        std::string const & pattern,
        PortNameVector const & external_ports,
        bool out)
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
                std::string const & output_port =
                        out ? port_name : external_port;
                std::string const & input_port =
                        out ? external_port : port_name;

                int error = jack_connect(_client, output_port.c_str(),
                                                  input_port.c_str());

                if (error && error != EEXIST) {
                    std::cerr << "could not connect " << output_port
                              << " to " << input_port << std::endl;
                }

                ++count;
            }
        }
        return count;
    }
    catch (das::regex::compile_error & ex) {
        throw std::runtime_error(das::make_string()
                << "failed to parse regular expression '"
                << pattern << "': " << ex.what());
    }
}


int JACKBackend::process_(jack_nframes_t nframes, void *arg)
{
    JACKBackend *that = static_cast<JACKBackend*>(arg);

    // read events from all input ports, and order them by frame
    that->fill_input_queue(nframes);

    std::fill(that->_last_written_frame.begin(),
              that->_last_written_frame.end(), 0);

    int r = that->process(nframes);

    that->_current_frame += nframes;
    return r;
}


void JACKBackend::fill_input_queue(jack_nframes_t nframes)
{
    ASSERT(_input_queue.empty());

    for (unsigned int port = 0; port != _in_ports.size(); ++port) {
        void *port_buffer = jack_port_get_buffer(_in_ports[port], nframes);

        for (unsigned int n = 0;
                n != jack_midi_get_event_count(port_buffer); ++n) {
            jack_midi_event_t jack_ev;
            VERIFY(!jack_midi_event_get(&jack_ev, port_buffer, n));

            MidiEvent ev = buffer_to_midi_event(
                                    jack_ev.buffer, jack_ev.size,
                                    port, _current_frame + jack_ev.time);
            _input_queue.push(ev);
        }
    }
}


void JACKBackend::clear_buffers(jack_nframes_t nframes)
{
    for (unsigned int n = 0; n < _out_ports.size(); ++n) {
        void *port_buffer = jack_port_get_buffer(_out_ports[n], nframes);
        jack_midi_clear_buffer(port_buffer);
    }
}


bool JACKBackend::read_event(MidiEvent & ev, jack_nframes_t /*nframes*/)
{
    if (!_input_queue.empty()) {
        ev = _input_queue.top();
        _input_queue.pop();
        return true;
    } else {
        return false;
    }
}


bool JACKBackend::write_event(MidiEvent const & ev, jack_nframes_t nframes)
{
    unsigned char data[config::JACK_MAX_EVENT_SIZE];
    std::size_t len = sizeof(data);
    int port;
    uint64_t frame;

    VERIFY(midi_event_to_buffer(ev, data, len, port, frame));

    void *port_buffer = jack_port_get_buffer(_out_ports[port], nframes);

    if (!len || len > jack_midi_max_event_size(port_buffer)) {
        return false;
    }

    // the frame within the current period at which the event will be written
    jack_nframes_t write_at_frame;

    if (frame >= _current_frame) {
        // event received within current period, zero delay
        write_at_frame = frame - _current_frame;
    } else if (frame >= _current_frame - nframes) {
        // event received during last period, exactly one period delay
        // (minimize jitter)
        write_at_frame = frame - _current_frame + nframes;
    } else {
        // event is older, send as soon as possible (minimize latency)
        write_at_frame = 0;
    }

    // if events would be out of order, simply increase this event's frame
    // to be equal to that of the most recently written event.
    // this should only happen in the rare cases where output_event() is
    // called directly from Python.
    if (jack_midi_get_event_count(port_buffer) &&
            write_at_frame < _last_written_frame[port]) {
        write_at_frame = _last_written_frame[port];
    }

    if (!jack_midi_event_write(port_buffer, write_at_frame, data, len)) {
        _last_written_frame[port] = write_at_frame;
        return true;
    } else {
        return false;
    }
}


} // backend
} // mididings
