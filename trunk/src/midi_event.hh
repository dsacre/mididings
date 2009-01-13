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

#ifndef _MIDI_EVENT_HH
#define _MIDI_EVENT_HH

#include <boost/cstdint.hpp>


enum MidiEventType
{
    MIDI_EVENT_NONE       = 0,
    MIDI_EVENT_NOTEON     = 1 << 0,
    MIDI_EVENT_NOTEOFF    = 1 << 1,
    MIDI_EVENT_NOTE       = MIDI_EVENT_NOTEON | MIDI_EVENT_NOTEOFF,
    MIDI_EVENT_CTRL       = 1 << 2,
    MIDI_EVENT_PITCHBEND  = 1 << 3,
    MIDI_EVENT_AFTERTOUCH = 1 << 4,
    MIDI_EVENT_PROGRAM    = 1 << 5,
    MIDI_EVENT_DUMMY      = 1 << 6,
    MIDI_EVENT_ANY        = ~0,
};

typedef unsigned int MidiEventTypes;


struct MidiEvent
{
    MidiEvent()
      : type(MIDI_EVENT_NONE)
      , port(0)
      , channel(0)
      , data1(0)
      , data2(0)
    {
    }

    MidiEvent(MidiEventType type_, int port_, int channel_, int data1_, int data2_)
      : type(type_)
      , port(port_)
      , channel(channel_)
      , data1(data1_)
      , data2(data2_)
    {
    }

    MidiEventType type;
    int port;
    int channel;

    union {
        struct {
            int note;
            int velocity;
        } note;

        struct {
            int param;
            int value;
        } ctrl;

        struct {
            int data1;
            int data2;
        };
    };

    uint64_t frame;
};


inline bool operator==(MidiEvent const & lhs, MidiEvent const & rhs)
{
    return (lhs.type == rhs.type &&
            lhs.port == rhs.port &&
            lhs.channel == rhs.channel &&
            lhs.data1 == rhs.data1 &&
            lhs.data2 == rhs.data2);
}


#endif // _MIDI_EVENT_HH
