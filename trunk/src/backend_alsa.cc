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

#include "backend_alsa.hh"
#include "midi_event.hh"

#include <alsa/asoundlib.h>

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
    if (snd_seq_open(&_seq_handle, "hw", SND_SEQ_OPEN_DUPLEX, 0) < 0) {
        throw BackendError("error opening alsa sequencer");
    }

    snd_seq_set_client_name(_seq_handle, client_name.c_str());

    // create input ports
    for (int n = 0; n < static_cast<int>(in_ports.size()); n++) {
        int id = snd_seq_create_simple_port(_seq_handle, in_ports[n].c_str(),
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
        int id = snd_seq_create_simple_port(_seq_handle, out_ports[n].c_str(),
                        SND_SEQ_PORT_CAP_READ | SND_SEQ_PORT_CAP_SUBS_READ,
                        SND_SEQ_PORT_TYPE_APPLICATION);

        if (id < 0) {
            throw BackendError("error creating sequencer output port");
        }

        _portid_out[n] = id;
    }
}


BackendAlsa::~BackendAlsa()
{
    if (_thrd) {
        terminate_thread();
        _thrd->join();
    }

    BOOST_FOREACH (int i, _portid_in) {
        snd_seq_delete_port(_seq_handle, i);
    }

    BOOST_FOREACH (int i, _portid_out) {
        snd_seq_delete_port(_seq_handle, i);
    }

    snd_seq_close(_seq_handle);
}


void BackendAlsa::start(InitFunction init, CycleFunction cycle)
{
    snd_seq_drop_input(_seq_handle);

    _thrd.reset(new boost::thread((
        boost::lambda::bind(init),
        boost::lambda::bind(cycle)
    )));
}


MidiEvent BackendAlsa::alsa_to_midi_event(snd_seq_event_t const & alsa_ev)
{
    MidiEvent ev;

    ev.port = _portid_in_rev[alsa_ev.dest.port];

    switch (alsa_ev.type) {
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
      default:
//        DEBUG_PRINT("event type " << static_cast<int>(alsa_ev.type) << " isn't handled");
        ev.type = MIDI_EVENT_NONE;
        break;
    }

    return ev;
}


snd_seq_event_t BackendAlsa::midi_event_to_alsa(MidiEvent const & ev)
{
    ASSERT(ev.type != MIDI_EVENT_NONE);
    ASSERT((uint)ev.port < _portid_out.size());
    if (ev.type != MIDI_EVENT_PITCHBEND) {
        ASSERT(ev.data1 >= 0x0 && ev.data1 <= 0x7f);
        ASSERT(ev.data2 >= 0x0 && ev.data2 <= 0x7f);
    } else {
        ASSERT(ev.data2 >= -8192 && ev.data2 <= 8191);
    }

    snd_seq_event_t alsa_ev;
    snd_seq_ev_clear(&alsa_ev);

    switch (ev.type) {
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
      default:
//        DEBUG_PRINT("unhandled event");
        break;
    }

    return alsa_ev;
}


bool BackendAlsa::input_event(MidiEvent & ev)
{
    snd_seq_event_t *alsa_ev;

    for (;;) {
        snd_seq_event_input(_seq_handle, &alsa_ev);

        if (alsa_ev) {
            // check for program termination
            if (alsa_ev->type == SND_SEQ_EVENT_USR0) {
                return false;
            }

            // convert event from alsa
            ev = alsa_to_midi_event(*alsa_ev);

            if (ev.type != MIDI_EVENT_NONE) {
                return true;
            }
        }
    }
}


void BackendAlsa::output_event(MidiEvent const & ev)
{
    snd_seq_event_t alsa_ev = midi_event_to_alsa(ev);

    snd_seq_ev_set_subs(&alsa_ev);
    snd_seq_ev_set_direct(&alsa_ev);
    snd_seq_ev_set_source(&alsa_ev, _portid_out[ev.port]);
    snd_seq_event_output_buffer(_seq_handle, &alsa_ev);
}


void BackendAlsa::flush_output()
{
    snd_seq_drain_output(_seq_handle);
}


void BackendAlsa::terminate_thread()
{
    // send event to ourselves to make snd_seq_event_input() return
    snd_seq_event_t ev;
    snd_seq_ev_clear(&ev);

    snd_seq_ev_set_direct(&ev);
    ev.type = SND_SEQ_EVENT_USR0;
    ev.source.port = _portid_out[0];
    ev.dest.client = snd_seq_client_id(_seq_handle);
    ev.dest.port = _portid_in[0];
    snd_seq_event_output_direct(_seq_handle, &ev);
}
