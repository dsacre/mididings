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
#include "backend/alsa.hh"
#include "midi_event.hh"

#include <alsa/asoundlib.h>

#include <iostream>
#include <unistd.h>

#include <boost/foreach.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/lambda/lambda.hpp>
#include <boost/lambda/bind.hpp>

#include "util/string.hh"
#include "util/debug.hh"


namespace Mididings {
namespace Backend {


ALSABackend::ALSABackend(std::string const & client_name,
                         PortNameVector const & in_port_names,
                         PortNameVector const & out_port_names)
{
    ASSERT(!client_name.empty());
    ASSERT(!in_port_names.empty());
    ASSERT(!out_port_names.empty());

    // create sequencer client
    if (snd_seq_open(&_seq, "hw", SND_SEQ_OPEN_DUPLEX, 0) < 0) {
        throw Error("error opening alsa sequencer");
    }

    snd_seq_set_client_name(_seq, client_name.c_str());

    // create input ports
    BOOST_FOREACH (std::string const & port_name, in_port_names) {
        int id = snd_seq_create_simple_port(_seq, port_name.c_str(),
                        SND_SEQ_PORT_CAP_WRITE | SND_SEQ_PORT_CAP_SUBS_WRITE,
                        SND_SEQ_PORT_TYPE_APPLICATION);

        if (id < 0) {
            throw Error("error creating sequencer input port");
        }

        int index = &port_name - &in_port_names[0];

        _in_ports.push_back(id);
        _in_ports_rev[id] = index;
    }

    // create output ports
    BOOST_FOREACH (std::string const & port_name, out_port_names) {
        int id = snd_seq_create_simple_port(_seq, port_name.c_str(),
                        SND_SEQ_PORT_CAP_READ | SND_SEQ_PORT_CAP_SUBS_READ,
                        SND_SEQ_PORT_TYPE_APPLICATION);

        if (id < 0) {
            throw Error("error creating sequencer output port");
        }

        _out_ports.push_back(id);
    }

    // initialize MIDI event parser.
    // we don't use the parser for sysex, so a 12 byte buffer will do
    if (snd_midi_event_new(12, &_parser)) {
        throw Error("error initializing MIDI event parser");
    }
    snd_midi_event_init(_parser);
    snd_midi_event_no_status(_parser, 1);
}


ALSABackend::~ALSABackend()
{
    snd_midi_event_free(_parser);

    BOOST_FOREACH (int i, _in_ports) {
        snd_seq_delete_port(_seq, i);
    }

    BOOST_FOREACH (int i, _out_ports) {
        snd_seq_delete_port(_seq, i);
    }

    snd_seq_close(_seq);
}


void ALSABackend::connect_ports(PortConnectionMap const & in_port_connections,
                                PortConnectionMap const & out_port_connections)
{
    connect_ports_impl(in_port_connections, _in_ports, false);
    connect_ports_impl(out_port_connections, _out_ports, true);
}


void ALSABackend::connect_ports_impl(PortConnectionMap const & port_connections, PortIdVector const & ports, bool out)
{
    if (port_connections.empty()) return;

    // get all JACK MIDI ports we could connect to
    ClientPortInfoVector external_ports = get_external_ports(!out);

    // for each of our ports...
    BOOST_FOREACH (int port, ports) {
        snd_seq_port_info_t *port_info;
        snd_seq_port_info_alloca(&port_info);

        snd_seq_get_port_info(_seq, port, port_info);
        std::string port_name = snd_seq_port_info_get_name(port_info);

        PortConnectionMap::const_iterator element = port_connections.find(port_name);

        // break if no connections are defined for this port
        if (element == port_connections.end()) break;

        // for each regex pattern defined for this port...
        BOOST_FOREACH (std::string const & pattern, element->second) {
            // connect to all ports that match the pattern
            if (connect_matching_ports(port, port_name, pattern, external_ports, out) == 0) {
                std::cerr << "regular expression '" << pattern << "' didn't match any ports" << std::endl;
            }
        }
    }
}


int ALSABackend::connect_matching_ports(int port, std::string const & port_name, std::string const & pattern,
                                        ClientPortInfoVector const & external_ports, bool out)
{
    snd_seq_client_info_t *client_info;
    snd_seq_client_info_alloca(&client_info);
    snd_seq_get_client_info(_seq, client_info);

    std::string client_name = snd_seq_client_info_get_name(client_info);
    int client_id = snd_seq_client_info_get_client(client_info);

    try {
        // compile pattern into regex object
        das::regex regex(pattern, true);
        int count = 0;

        // for each external ALSA MIDI port we might connect to...
        BOOST_FOREACH (ClientPortInfo const & external_port, external_ports) {
            std::string external_client_id = boost::lexical_cast<std::string>(external_port.client_id);
            std::string external_port_id = boost::lexical_cast<std::string>(external_port.port_id);

            // check if any combination of client/port and name/id matches regex
            if (regex.match(external_client_id + ":" + external_port_id) ||
                regex.match(external_client_id + ":" + external_port.port_name) ||
                regex.match(external_port.client_name + ":" + external_port_id) ||
                regex.match(external_port.client_name + ":" + external_port.port_name))
            {
                // connect ports
                snd_seq_addr_t self, other;
                self.client = client_id;
                self.port = port;
                other.client = external_port.client_id;
                other.port = external_port.port_id;

                snd_seq_port_subscribe_t *subscribe;
                snd_seq_port_subscribe_alloca(&subscribe);
                snd_seq_port_subscribe_set_sender(subscribe, out ? &self : &other);
                snd_seq_port_subscribe_set_dest(subscribe, out ? & other : &self);

                if (snd_seq_subscribe_port(_seq, subscribe) != 0 &&
                    snd_seq_get_port_subscription(_seq, subscribe) != 0)
                {
                    std::string self_full = client_name + ":" + port_name;
                    std::string other_full = external_port.client_name + ":" + external_port.port_name;

                    std::cerr << "could not connect " << (out ? self_full : other_full)
                              << " to " << (out ? other_full : self_full) << std::endl;
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


ALSABackend::ClientPortInfoVector ALSABackend::get_external_ports(bool out)
{
    unsigned int port_flags = out ? SND_SEQ_PORT_CAP_READ | SND_SEQ_PORT_CAP_SUBS_READ
                                  : SND_SEQ_PORT_CAP_WRITE | SND_SEQ_PORT_CAP_SUBS_WRITE;
    ClientPortInfoVector vec;

    snd_seq_client_info_t *client_info;
    snd_seq_client_info_alloca(&client_info);
    snd_seq_client_info_set_client(client_info, -1);

    while (snd_seq_query_next_client(_seq, client_info) == 0) {
        int client_id = snd_seq_client_info_get_client(client_info);
        std::string client_name = snd_seq_client_info_get_name(client_info);

        snd_seq_port_info_t *port_info;
        snd_seq_port_info_alloca(&port_info);
        snd_seq_port_info_set_client(port_info, client_id);
        snd_seq_port_info_set_port(port_info, -1);

        while (snd_seq_query_next_port(_seq, port_info) == 0) {
            unsigned int capability = snd_seq_port_info_get_capability(port_info);

            if (((capability & port_flags) == port_flags) &&
                ((capability & SND_SEQ_PORT_CAP_NO_EXPORT) == 0)) {
                int port_id = snd_seq_port_info_get_port(port_info);
                std::string port_name = snd_seq_port_info_get_name(port_info);

                ClientPortInfo info(client_id, port_id, client_name, port_name);
                vec.push_back(info);
            }
        }
    }

    return vec;
}


void ALSABackend::start(InitFunction init, CycleFunction cycle)
{
    // discard events which were received while processing wasn't ready
    snd_seq_drop_input(_seq);

    // start processing thread.
    // cycle doesn't return until the program is shut down
    _thread.reset(new boost::thread((
        boost::lambda::bind(init),
        boost::lambda::bind(cycle)
    )));
}


void ALSABackend::stop()
{
    if (_thread) {
        // send event to ourselves to make snd_seq_event_input() return
        snd_seq_event_t ev;
        snd_seq_ev_clear(&ev);

        snd_seq_ev_set_direct(&ev);
        ev.type = SND_SEQ_EVENT_USR0;
        ev.source.port = _out_ports[0];
        ev.dest.client = snd_seq_client_id(_seq);
        ev.dest.port = _in_ports[0];
        snd_seq_event_output_direct(_seq, &ev);

        // wait for event processing thread to terminate
        _thread->join();
    }
}


void ALSABackend::alsa_to_midi_event(MidiEvent & ev, snd_seq_event_t const & alsa_ev)
{
    ev.port = _in_ports_rev[alsa_ev.dest.port];

    switch (alsa_ev.type)
    {
      case SND_SEQ_EVENT_NOTEON:
        ev.type = alsa_ev.data.note.velocity ? MIDI_EVENT_NOTEON : MIDI_EVENT_NOTEOFF;
        ev.channel = alsa_ev.data.note.channel;
        ev.note.note = alsa_ev.data.note.note;
        ev.note.velocity = alsa_ev.data.note.velocity;
        break;

      case SND_SEQ_EVENT_NOTEOFF:
        ev.type = MIDI_EVENT_NOTEOFF;
        ev.channel = alsa_ev.data.note.channel;
        ev.note.note = alsa_ev.data.note.note;
        ev.note.velocity = alsa_ev.data.note.velocity;
        break;

      case SND_SEQ_EVENT_CONTROLLER:
        ev.type = MIDI_EVENT_CTRL;
        ev.channel = alsa_ev.data.control.channel;
        ev.ctrl.param = alsa_ev.data.control.param;
        ev.ctrl.value = alsa_ev.data.control.value;
        break;

      case SND_SEQ_EVENT_PITCHBEND:
        ev.type = MIDI_EVENT_PITCHBEND;
        ev.channel = alsa_ev.data.control.channel;
        ev.ctrl.param = 0;
        ev.ctrl.value = alsa_ev.data.control.value;
        break;

      case SND_SEQ_EVENT_CHANPRESS:
        ev.type = MIDI_EVENT_AFTERTOUCH;
        ev.channel = alsa_ev.data.control.channel;
        ev.ctrl.param = 0;
        ev.ctrl.value = alsa_ev.data.control.value;
        break;

      case SND_SEQ_EVENT_PGMCHANGE:
        ev.type = MIDI_EVENT_PROGRAM;
        ev.channel = alsa_ev.data.control.channel;
        ev.ctrl.param = 0;
        ev.ctrl.value = alsa_ev.data.control.value;
        break;

      case SND_SEQ_EVENT_SYSEX:
        alsa_to_midi_event_sysex(ev, alsa_ev);
        break;

      case SND_SEQ_EVENT_KEYPRESS:
      case SND_SEQ_EVENT_QFRAME:
      case SND_SEQ_EVENT_SONGPOS:
      case SND_SEQ_EVENT_SONGSEL:
      case SND_SEQ_EVENT_TUNE_REQUEST:
      case SND_SEQ_EVENT_CLOCK:
      case SND_SEQ_EVENT_START:
      case SND_SEQ_EVENT_CONTINUE:
      case SND_SEQ_EVENT_STOP:
      case SND_SEQ_EVENT_SENSING:
      case SND_SEQ_EVENT_RESET:
        // use generic decoder for other event types (because i'm lazy)
        alsa_to_midi_event_generic(ev, alsa_ev);
        break;

      default:
        // who the hell are you?
        ev.type = MIDI_EVENT_NONE;
        break;
    }
}


void ALSABackend::alsa_to_midi_event_sysex(MidiEvent & ev, snd_seq_event_t const & alsa_ev)
{
    unsigned char *ptr = static_cast<unsigned char *>(alsa_ev.data.ext.ptr);
    std::size_t len = alsa_ev.data.ext.len;

    if (ptr[0] == 0xf0) {
        // new sysex started, insert into buffer
        _sysex_buffer.erase(ev.port);
        _sysex_buffer.insert(std::make_pair(ev.port, SysExDataPtr(new SysExData(ptr, ptr + len))));
    }
    else if (_sysex_buffer.find(ev.port) != _sysex_buffer.end()) {
        // previous sysex continued, append to buffer
        _sysex_buffer[ev.port]->insert(_sysex_buffer[ev.port]->end(), ptr, ptr + len);
    }

    if (_sysex_buffer[ev.port]->back() == 0xf7) {
        // end of sysex, assign complete event
        ev.type = MIDI_EVENT_SYSEX;
        ev.channel = 0;
        ev.data1 = 0;
        ev.data2 = 0;
        ev.sysex = _sysex_buffer[ev.port];
        // delete from buffer
        _sysex_buffer.erase(ev.port);
    } else {
        // sysex still incomplete
        ev.type = MIDI_EVENT_NONE;
    }
}


void ALSABackend::alsa_to_midi_event_generic(MidiEvent & ev, snd_seq_event_t const & alsa_ev)
{
    unsigned char buf[12];

    snd_midi_event_reset_decode(_parser);
    std::size_t len = snd_midi_event_decode(_parser, buf, sizeof(buf), &alsa_ev);

    ev = buffer_to_midi_event(buf, len, _in_ports_rev[alsa_ev.dest.port], 0);
}


void ALSABackend::midi_event_to_alsa(snd_seq_event_t & alsa_ev, MidiEvent const & ev, std::size_t & count)
{
    ASSERT(ev.type != MIDI_EVENT_NONE);
    ASSERT((uint)ev.port < _out_ports.size());
    if (ev.type != MIDI_EVENT_PITCHBEND) {
        ASSERT(ev.data1 >= 0x0 && ev.data1 <= 0x7f);
        ASSERT(ev.data2 >= 0x0 && ev.data2 <= 0x7f);
    } else {
        ASSERT(ev.data2 >= -8192 && ev.data2 <= 8191);
    }

    snd_seq_ev_clear(&alsa_ev);

    switch (ev.type)
    {
      case MIDI_EVENT_NOTEON:
        snd_seq_ev_set_noteon(&alsa_ev, ev.channel, ev.note.note, ev.note.velocity);
        break;

      case MIDI_EVENT_NOTEOFF:
        snd_seq_ev_set_noteoff(&alsa_ev, ev.channel, ev.note.note, ev.note.velocity);
        break;

      case MIDI_EVENT_CTRL:
        snd_seq_ev_set_controller(&alsa_ev, ev.channel, ev.ctrl.param, ev.ctrl.value);
        break;

      case MIDI_EVENT_PITCHBEND:
        snd_seq_ev_set_pitchbend(&alsa_ev, ev.channel, ev.ctrl.value);
        break;

      case MIDI_EVENT_AFTERTOUCH:
        snd_seq_ev_set_chanpress(&alsa_ev, ev.channel, ev.ctrl.value);
        break;

      case MIDI_EVENT_PROGRAM:
        snd_seq_ev_set_pgmchange(&alsa_ev, ev.channel, ev.ctrl.value);
        break;

      case MIDI_EVENT_SYSEX:
        midi_event_to_alsa_sysex(alsa_ev, ev, count);
        break;

      default:
        // use generic encoder for other event types
        midi_event_to_alsa_generic(alsa_ev, ev);
        break;
    }
}


void ALSABackend::midi_event_to_alsa_sysex(snd_seq_event_t & alsa_ev, MidiEvent const & ev, std::size_t & count)
{
    unsigned char const * data = &ev.sysex->front();
    std::size_t size = ev.sysex->size();

    // number of bytes that will be sent in this chunk
    std::size_t len = std::min(size - count, Config::ALSA_SYSEX_CHUNK_SIZE);

    // let's hope the alsa guys just "forgot" that little const keyword...
    snd_seq_ev_set_sysex(&alsa_ev, len, const_cast<void *>(static_cast<void const *>(data + count)));

    count += len;

    if (count >= size) {
        // done, this was the last chunk
        count = 0;
    }
}


void ALSABackend::midi_event_to_alsa_generic(snd_seq_event_t & alsa_ev, MidiEvent const & ev)
{
    // maximum size of non-sysex sequencer events is 12 bytes
    unsigned char buf[12];
    std::size_t len = 12;
    int port;
    uint64_t frame;

    midi_event_to_buffer(ev, buf, len, port, frame);

    snd_midi_event_reset_encode(_parser);
    snd_midi_event_encode(_parser, buf, len, &alsa_ev);
}


bool ALSABackend::input_event(MidiEvent & ev)
{
    snd_seq_event_t *alsa_ev;

    // loop until we've received an event we're interested in
    for (;;) {
        if (snd_seq_event_input(_seq, &alsa_ev) < 0 || !alsa_ev) {
            DEBUG_PRINT("couldn't retrieve ALSA sequencer event");
            continue;
        }

        // check for program termination
        if (alsa_ev->type == SND_SEQ_EVENT_USR0) {
            return false;
        }

        // convert event from alsa
        alsa_to_midi_event(ev, *alsa_ev);

        if (ev.type != MIDI_EVENT_NONE) {
            return true;
        }
    }
}


void ALSABackend::output_event(MidiEvent const & ev)
{
    snd_seq_event_t alsa_ev;

    // number of bytes already sent (for sysex), or zero if the whole event was sent
    std::size_t count = 0;

    do {
        midi_event_to_alsa(alsa_ev, ev, count);

        snd_seq_ev_set_subs(&alsa_ev);
        snd_seq_ev_set_direct(&alsa_ev);
        snd_seq_ev_set_source(&alsa_ev, _out_ports[ev.port]);

        if (snd_seq_event_output_direct(_seq, &alsa_ev) < 0) {
            DEBUG_PRINT("couldn't output event to ALSA sequencer buffer");
        }

        if (count) {
            // wait as long as it takes for one chunk to be transmitted at MIDI baud rate.
            // constant copied from Simple Sysexxer by Christoph Eckert.
            ::usleep(Config::ALSA_SYSEX_CHUNK_SIZE * 352);
        }
    } while (count);
}


} // Backend
} // Mididings
