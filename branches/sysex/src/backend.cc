/*
 * mididings
 *
 * Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "backend.hh"


MidiEvent Backend::buffer_to_midi_event(unsigned char *data, int port, uint64_t frame)
{
    MidiEvent ev;

    ev.frame = frame;
    ev.port = port;
    ev.channel = data[0] & 0x0f;

    switch (data[0] & 0xf0)
    {
      case 0x90:
        ev.type = data[2] ? MIDI_EVENT_NOTEON : MIDI_EVENT_NOTEOFF;
        ev.note.note = data[1];
        ev.note.velocity = data[2];
        break;
      case 0x80:
        ev.type = MIDI_EVENT_NOTEOFF;
        ev.note.note = data[1];
        ev.note.velocity = data[2];
        break;
      case 0xb0:
        ev.type = MIDI_EVENT_CTRL;
        ev.ctrl.param = data[1];
        ev.ctrl.value = data[2];
        break;
      case 0xe0:
        ev.type = MIDI_EVENT_PITCHBEND;
        ev.ctrl.param = 0;
        ev.ctrl.value = (data[2] << 7 | data[1]) - 8192;
        break;
      case 0xd0:
        ev.type = MIDI_EVENT_AFTERTOUCH;
        ev.ctrl.param = 0;
        ev.ctrl.value = data[1];
        break;
      case 0xc0:
        ev.type = MIDI_EVENT_PROGRAM;
        ev.ctrl.param = 0;
        ev.ctrl.value = data[1];
        break;
      default:
        ev.type = MIDI_EVENT_NONE;
        break;
    }

    return ev;
}


void Backend::midi_event_to_buffer(MidiEvent const & ev, unsigned char *data, std::size_t & len, int & port, uint64_t & frame)
{
    frame = ev.frame;
    port = ev.port;
    data[0] = ev.channel;

    switch (ev.type)
    {
      case MIDI_EVENT_NOTEON:
        len = 3;
        data[0] |= 0x90;
        data[1] = ev.note.note;
        data[2] = ev.note.velocity;
        break;
      case MIDI_EVENT_NOTEOFF:
        len = 3;
        data[0] |= 0x80;
        data[1] = ev.note.note;
        data[2] = ev.note.velocity;
        break;
      case MIDI_EVENT_CTRL:
        len = 3;
        data[0] |= 0xb0;
        data[1] = ev.ctrl.param;
        data[2] = ev.ctrl.value;
        break;
      case MIDI_EVENT_PITCHBEND:
        len = 3;
        data[0] |= 0xe0;
        data[1] = (ev.ctrl.value + 8192) % 128;
        data[2] = (ev.ctrl.value + 8192) / 128;
        break;
      case MIDI_EVENT_AFTERTOUCH:
        len = 2;
        data[0] |= 0xd0;
        data[1] = ev.ctrl.value;
        break;
      case MIDI_EVENT_PROGRAM:
        len = 2;
        data[0] |= 0xc0;
        data[1] = ev.ctrl.value;
        break;
      default:
        len = 0;
    }
}
