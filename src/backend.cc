/*
 * mididings
 *
 * Copyright (C) 2007  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "backend.h"
#include "util.h"

#include <iostream>

using namespace std;


string Backend::dump_event(const MidiEvent & ev)
{
    switch (ev.type)
    {
      case MIDI_EVENT_NOTEON:
        return make_string() << "note on: port " << ev.port << ", channel " << ev.channel
                             << ", note " << ev.note.note << ", velocity " << ev.note.velocity;
        break;

      case MIDI_EVENT_NOTEOFF:
        return make_string() << "note off: port " << ev.port << ", channel " << ev.channel
                             << ", note " << ev.note.note << ", velocity " << ev.note.velocity;
        break;

      case MIDI_EVENT_CONTROLLER:
        return make_string() << "ctrl: port " << ev.port << ", channel " << ev.channel
                             << ", param " << ev.ctrl.param << ", value " << ev.ctrl.value;
        break;
      case MIDI_EVENT_PITCHBEND:
        return make_string() << "pitch bend: port " << ev.port << ", channel " << ev.channel
                             << ", value " << ev.ctrl.value;
        break;
      case MIDI_EVENT_PGMCHANGE:
        return make_string() << "program change: port " << ev.port << ", channel " << ev.channel
                             << ", value " << ev.ctrl.value;
        break;
      default:
        return "unknown event type";
    }
}


void Backend::dump_incoming_event(const MidiEvent & ev)
{
    if (_debug) {
        cout << "in: " << dump_event(ev) << endl;
    }
}


void Backend::dump_outgoing_events(const std::vector<MidiEvent> & evs)
{
    if (_debug) {
        for (vector<MidiEvent>::const_iterator i = evs.begin(); i != evs.end(); ++i) {
            cout << "out: " << dump_event(*i) << endl;
        }
    }
}
