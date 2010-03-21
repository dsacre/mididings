/*
 * mididings
 *
 * Copyright (C) 2008-2010  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "backend_alsa.hh"
#include "midi_event.hh"
#include "config.hh"

#include <alsa/asoundlib.h>

#include <unistd.h>

#include <boost/foreach.hpp>
#include <boost/lambda/lambda.hpp>
#include <boost/lambda/bind.hpp>

#include "util/debug.hh"


BackendAlsa::BackendAlsa(std::string const & client_name,
                         std::vector<std::string> const & in_ports,
                         std::vector<std::string> const & out_ports)
  : _portid_in(in_ports.size())
  , _portid_out(out_ports.size())
{
    ASSERT(!client_name.empty());
    ASSERT(!in_ports.empty());
    ASSERT(!out_ports.empty());

    // create sequencer client
    if (snd_seq_open(&_seq, "hw", SND_SEQ_OPEN_DUPLEX, 0) < 0) {
        throw BackendError("error opening alsa sequencer");
    }

    snd_seq_set_client_name(_seq, client_name.c_str());

    // create input ports
    for (int n = 0; n < static_cast<int>(in_ports.size()); n++) {
        int id = snd_seq_create_simple_port(_seq, in_ports[n].c_str(),
                        SND_SEQ_PORT_CAP_WRITE | SND_SEQ_PORT_CAP_SUBS_WRITE,
                        SND_SEQ_PORT_TYPE_APPLICATION);

        if (id < 0) {
            throw BackendError("error creating sequencer input port");
        }

        _portid_in[n] = id;
        _portid_in_rev[id] = n;
    }

    // create output ports
    for (int n = 0; n < static_cast<int>(out_ports.size()); n++) {
        int id = snd_seq_create_simple_port(_seq, out_ports[n].c_str(),
                        SND_SEQ_PORT_CAP_READ | SND_SEQ_PORT_CAP_SUBS_READ,
                        SND_SEQ_PORT_TYPE_APPLICATION);

        if (id < 0) {
            throw BackendError("error creating sequencer output port");
        }

        _portid_out[n] = id;
    }

    // initialize MIDI event parser.
    // we don't use the parser for sysex, so a 12 byte buffer will do
    if (snd_midi_event_new(12, &_parser)) {
        throw BackendError("error initializing MIDI event parser");
    }
    snd_midi_event_init(_parser);
    snd_midi_event_no_status(_parser, 1);
}


BackendAlsa::~BackendAlsa()
{
    if (_thrd) {
        // notify event processing thread and wait for it to terminate
        terminate_thread();
        _thrd->join();
    }

    snd_midi_event_free(_parser);

    BOOST_FOREACH (int i, _portid_in) {
        snd_seq_delete_port(_seq, i);
    }

    BOOST_FOREACH (int i, _portid_out) {
        snd_seq_delete_port(_seq, i);
    }

    snd_seq_close(_seq);
}


void BackendAlsa::start(InitFunction init, CycleFunction cycle)
{
    // discard events which were received while processing wasn't ready
    snd_seq_drop_input(_seq);

    // start processing thread.
    // cycle doesn't return until the program is shut down
    _thrd.reset(new boost::thread((
        boost::lambda::bind(init),
        boost::lambda::bind(cycle)
    )));
}


void BackendAlsa::alsa_to_midi_event(MidiEvent & ev, snd_seq_event_t const & alsa_ev)
{
    ev.port = _portid_in_rev[alsa_ev.dest.port];

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


void BackendAlsa::alsa_to_midi_event_sysex(MidiEvent & ev, snd_seq_event_t const & alsa_ev)
{
    unsigned char *ptr = static_cast<unsigned char *>(alsa_ev.data.ext.ptr);
    std::size_t len = alsa_ev.data.ext.len;

    if (ptr[0] == 0xf0) {
        // new sysex started, insert into buffer
        _sysex_buffer.erase(ev.port);
        _sysex_buffer.insert(std::make_pair(ev.port, MidiEvent::SysExPtr(new MidiEvent::SysExData(ptr, ptr + len))));
    }
    else if (_sysex_buffer.find(ev.port) != _sysex_buffer.end()) {
        // previous sysex continued, append to buffer
        _sysex_buffer[ev.port]->append(ptr, ptr + len);
    }

    MidiEvent::SysExData const & s = *_sysex_buffer[ev.port];

    if (static_cast<unsigned char>(s[s.size() - 1]) == 0xf7) {
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


void BackendAlsa::alsa_to_midi_event_generic(MidiEvent & ev, snd_seq_event_t const & alsa_ev)
{
    unsigned char buf[12];

    snd_midi_event_reset_decode(_parser);
    std::size_t len = snd_midi_event_decode(_parser, buf, sizeof(buf), &alsa_ev);

    ev = buffer_to_midi_event(buf, len, _portid_in_rev[alsa_ev.dest.port], 0);
}


void BackendAlsa::midi_event_to_alsa(snd_seq_event_t & alsa_ev, MidiEvent const & ev, std::size_t & count)
{
    ASSERT(ev.type != MIDI_EVENT_NONE);
    ASSERT((uint)ev.port < _portid_out.size());
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


void BackendAlsa::midi_event_to_alsa_sysex(snd_seq_event_t & alsa_ev, MidiEvent const & ev, std::size_t & count)
{
    char const * data = ev.sysex->c_str();
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


void BackendAlsa::midi_event_to_alsa_generic(snd_seq_event_t & alsa_ev, MidiEvent const & ev)
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


bool BackendAlsa::input_event(MidiEvent & ev)
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


void BackendAlsa::output_event(MidiEvent const & ev)
{
    snd_seq_event_t alsa_ev;

    // number of bytes already sent (for sysex), or zero if the whole event was sent
    std::size_t count = 0;

    do {
        midi_event_to_alsa(alsa_ev, ev, count);

        snd_seq_ev_set_subs(&alsa_ev);
        snd_seq_ev_set_direct(&alsa_ev);
        snd_seq_ev_set_source(&alsa_ev, _portid_out[ev.port]);

        if (snd_seq_event_output_direct(_seq, &alsa_ev) < 0) {
            DEBUG_PRINT("couldn't output event to ALSA sequencer buffer");
        }

        if (count) {
            // wait as long as it takes for one chunk to be transmitted at MIDI baud rate.
            // constant copied from from Simple Sysexxer by Christoph Eckert.
            ::usleep(Config::ALSA_SYSEX_CHUNK_SIZE * 352);
        }
    } while (count);
}


void BackendAlsa::terminate_thread()
{
    // send event to ourselves to make snd_seq_event_input() return
    snd_seq_event_t ev;
    snd_seq_ev_clear(&ev);

    snd_seq_ev_set_direct(&ev);
    ev.type = SND_SEQ_EVENT_USR0;
    ev.source.port = _portid_out[0];
    ev.dest.client = snd_seq_client_id(_seq);
    ev.dest.port = _portid_in[0];
    snd_seq_event_output_direct(_seq, &ev);
}
