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

#include "setup.hh"
#include "midi_event.hh"

#include <alsa/asoundlib.h>

#include <algorithm>
#include <boost/lambda/bind.hpp>
#include <boost/lambda/lambda.hpp>

using namespace std;
using namespace boost::lambda;


BackendAlsa::BackendAlsa(const string & client_name,
                         const vector<string> & in_ports,
                         const vector<string> & out_ports)
  : _portid_in(in_ports.size()),
    _portid_out(out_ports.size())
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
    for (int n = 0; n < (int)in_ports.size(); n++) {
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
    for (int n = 0; n < (int)out_ports.size(); n++) {
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
    for_each(_portid_in.begin(), _portid_in.end(), bind(snd_seq_delete_port, _seq_handle, _1));
    for_each(_portid_out.begin(), _portid_out.end(), bind(snd_seq_delete_port, _seq_handle, _1));

    snd_seq_close(_seq_handle);
}


MidiEvent BackendAlsa::alsa_to_midi_event(const snd_seq_event_t & alsa_ev)
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
      case SND_SEQ_EVENT_PGMCHANGE:
        ev.type = MIDI_EVENT_PROGRAM;
        ev.channel = alsa_ev.data.control.channel;
        ev.ctrl.param = 0;
        ev.ctrl.value = alsa_ev.data.control.value;
        break;
      default:
//        DEBUG_PRINT("event type " << (int)alsa_ev.type << " isn't handled");
        ev.type = MIDI_EVENT_NONE;
        break;
    }

    return ev;
}


snd_seq_event_t BackendAlsa::midi_event_to_alsa(const MidiEvent & ev)
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
      case MIDI_EVENT_PROGRAM:
        snd_seq_ev_set_pgmchange(&alsa_ev, ev.channel, ev.ctrl.value);
        break;
      default:
//        DEBUG_PRINT("unhandled event");
        break;
    }

    return alsa_ev;
}


void BackendAlsa::run(Setup & setup)
{
    snd_seq_event_t *alsa_ev;

    // handle init events
    const Setup::MidiEventVector & out_events = setup.init_events();

    for (vector<MidiEvent>::const_iterator i = out_events.begin(); i != out_events.end(); ++i) {
        snd_seq_event_t alsa_ev = midi_event_to_alsa(*i);

        snd_seq_ev_set_subs(&alsa_ev);
        snd_seq_ev_set_direct(&alsa_ev);
        snd_seq_ev_set_source(&alsa_ev, _portid_out[i->port]);
        snd_seq_event_output_buffer(_seq_handle, &alsa_ev);
    }

    snd_seq_drain_output(_seq_handle);


    while (snd_seq_event_input(_seq_handle, &alsa_ev)) {
        if (!alsa_ev) {
            // terminated by user?
            return;
        }

        // convert event from alsa
        MidiEvent ev = alsa_to_midi_event(*alsa_ev);

        // discard unknown events
        if (ev.type == MIDI_EVENT_NONE) {
            continue;
        }

        //DEBUG_PRINT("in: " << ev.type << ": " << ev.port << " "
        //            << ev.channel << " " << ev.data1 << " " << ev.data2);

        // do all processing
        const Setup::MidiEventVector & out_events = setup.process(ev);

        // output all events to alsa
        for (vector<MidiEvent>::const_iterator i = out_events.begin(); i != out_events.end(); ++i) {
            //DEBUG_PRINT("out: " << i->type << ": " << i->port << " "
            //            << i->channel << " " << i->data1 << " " << i->data2);

            snd_seq_event_t alsa_ev = midi_event_to_alsa(*i);

            snd_seq_ev_set_subs(&alsa_ev);
            snd_seq_ev_set_direct(&alsa_ev);
            snd_seq_ev_set_source(&alsa_ev, _portid_out[i->port]);
            snd_seq_event_output_buffer(_seq_handle, &alsa_ev);
        }

        // flush event buffer
        snd_seq_drain_output(_seq_handle);
    }
}
