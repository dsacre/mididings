/*
 * midipatch
 *
 * Copyright (C) 2007  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "backend_alsa.h"

#include "setup.h"
#include "midi_event.h"

#include <alsa/asoundlib.h>
#include <iostream>

using namespace std;


BackendAlsa::BackendAlsa(const string & client_name,
                         int in_ports, int out_ports,
                         const vector<string> & in_portnames,
                         const vector<string> & out_portnames,
                         bool debug)
  : Backend(debug),
    _portid_in(in_ports),
    _portid_out(out_ports)
{
    ASSERT(in_portnames.size() == (uint)in_ports || in_portnames.empty());
    ASSERT(out_portnames.size() == (uint)out_ports || out_portnames.empty());

    // create sequencer client
    if (snd_seq_open(&_seq_handle, "hw", SND_SEQ_OPEN_DUPLEX, 0) < 0) {
        throw BackendError("error opening alsa sequencer");
    }

    snd_seq_set_client_name(_seq_handle, client_name.c_str());

    // create input ports
    for (int n = 0; n < in_ports; n++) {
        string port_name;

        if (in_portnames.empty())
            port_name = make_string() << "in_" << n;
        else
            port_name = in_portnames[n];

        int id = snd_seq_create_simple_port(_seq_handle, port_name.c_str(),
                    SND_SEQ_PORT_CAP_WRITE | SND_SEQ_PORT_CAP_SUBS_WRITE,
                    SND_SEQ_PORT_TYPE_APPLICATION);

        if (id < 0)
            throw BackendError("error creating sequencer input port");

        _portid_in[n] = id;
        _portid_in_rev[id] = n;
    }

    // create output ports
    for (int n = 0; n < out_ports; n++) {
        string port_name;

        if (out_portnames.empty())
            port_name = make_string() << "out_" << n;
        else
            port_name = out_portnames[n];

        int id = snd_seq_create_simple_port(_seq_handle, port_name.c_str(),
                SND_SEQ_PORT_CAP_READ | SND_SEQ_PORT_CAP_SUBS_READ,
                SND_SEQ_PORT_TYPE_APPLICATION);

        if (id < 0)
            throw BackendError("error creating sequencer output port");

        _portid_out[n] = id;
    }
}


BackendAlsa::~BackendAlsa()
{
    for (vector<int>::iterator i = _portid_in.begin(); i != _portid_in.end(); ++i) {
        snd_seq_delete_port(_seq_handle, *i);
    }
    for (vector<int>::iterator i = _portid_out.begin(); i != _portid_out.end(); ++i) {
        snd_seq_delete_port(_seq_handle, *i);
    }
    snd_seq_close(_seq_handle);
}


MidiEvent BackendAlsa::alsa_to_midi_event(const snd_seq_event_t & alsa_ev)
{
    MidiEvent ev;

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
        ev.type = MIDI_EVENT_CONTROLLER;
        ev.channel = alsa_ev.data.control.channel;
        ev.ctrl.param = alsa_ev.data.control.param;
        ev.ctrl.value = alsa_ev.data.control.value;
        break;
      case SND_SEQ_EVENT_PITCHBEND:
        ev.type = MIDI_EVENT_PITCHBEND;
        ev.channel = alsa_ev.data.control.channel;
        ev.ctrl.value = alsa_ev.data.control.value;
        break;
      case SND_SEQ_EVENT_PGMCHANGE:
        ev.type = MIDI_EVENT_PGMCHANGE;
        ev.channel = alsa_ev.data.control.channel;
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
    ASSERT(ev.data1 >= 0x0 && ev.data1 <= 0x7f);
    ASSERT(ev.data2 >= 0x0 && ev.data2 <= 0x7f);

    snd_seq_event_t alsa_ev;

    snd_seq_ev_clear(&alsa_ev);

    switch (ev.type)
    {
      case MIDI_EVENT_NOTEON:
        snd_seq_ev_set_noteon(&alsa_ev, ev.channel, ev.note.note, ev.note.velocity);
        break;
      case MIDI_EVENT_NOTEOFF:
        snd_seq_ev_set_noteoff(&alsa_ev, ev.channel, ev.note.note, ev.note.velocity);
        break;
      case MIDI_EVENT_CONTROLLER:
        snd_seq_ev_set_controller(&alsa_ev, ev.channel, ev.ctrl.param, ev.ctrl.value);
        break;
      case MIDI_EVENT_PITCHBEND:
        snd_seq_ev_set_pitchbend(&alsa_ev, ev.channel, ev.ctrl.value);
        break;
      case MIDI_EVENT_PGMCHANGE:
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

    while (snd_seq_event_input(_seq_handle, &alsa_ev))
    {
        if (alsa_ev == NULL) {
            return;
        }

        // convert event from alsa
        MidiEvent ev = alsa_to_midi_event(*alsa_ev);

        // discard unknown events
        if (ev.type == MIDI_EVENT_NONE)
            continue;

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
