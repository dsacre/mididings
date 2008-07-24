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

#ifndef _MIDI_EVENT_HH
#define _MIDI_EVENT_HH


enum MidiEventType
{
    MIDI_EVENT_NONE       = 0,
    MIDI_EVENT_NOTEON     = 1 << 0,
    MIDI_EVENT_NOTEOFF    = 1 << 1,
    MIDI_EVENT_NOTE       = MIDI_EVENT_NOTEON | MIDI_EVENT_NOTEOFF,
    MIDI_EVENT_CTRL       = 1 << 2,
    MIDI_EVENT_PITCHBEND  = 1 << 3,
    MIDI_EVENT_PROGRAM    = 1 << 4,
    MIDI_EVENT_ANY        = ~0,
};

typedef unsigned int MidiEventTypes;


struct MidiEvent
{
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
};


#endif // _MIDI_EVENT_HH
