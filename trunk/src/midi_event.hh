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

#ifndef MIDIDINGS_MIDI_EVENT_HH
#define MIDIDINGS_MIDI_EVENT_HH

#include <boost/cstdint.hpp>
#include <boost/shared_ptr.hpp>
#include <string>


namespace Mididings {


enum MidiEventType
{
    MIDI_EVENT_NONE             = 0,
    MIDI_EVENT_NOTEON           = 1 << 0,
    MIDI_EVENT_NOTEOFF          = 1 << 1,
    MIDI_EVENT_CTRL             = 1 << 2,
    MIDI_EVENT_PITCHBEND        = 1 << 3,
    MIDI_EVENT_AFTERTOUCH       = 1 << 4,
    MIDI_EVENT_POLY_AFTERTOUCH  = 1 << 5,
    MIDI_EVENT_PROGRAM          = 1 << 6,
    MIDI_EVENT_SYSEX            = 1 << 7,
    MIDI_EVENT_SYSCM_QFRAME     = 1 << 8,
    MIDI_EVENT_SYSCM_SONGPOS    = 1 << 9,
    MIDI_EVENT_SYSCM_SONGSEL    = 1 << 10,
    MIDI_EVENT_SYSCM_TUNEREQ    = 1 << 11,
    MIDI_EVENT_SYSRT_CLOCK      = 1 << 12,
    MIDI_EVENT_SYSRT_START      = 1 << 13,
    MIDI_EVENT_SYSRT_CONTINUE   = 1 << 14,
    MIDI_EVENT_SYSRT_STOP       = 1 << 15,
    MIDI_EVENT_SYSRT_SENSING    = 1 << 16,
    MIDI_EVENT_SYSRT_RESET      = 1 << 17,
    MIDI_EVENT_DUMMY            = 1 << 30,
    MIDI_EVENT_ANY              = ~0,
};

typedef unsigned int MidiEventTypes;


struct MidiEvent
{
    typedef std::string SysExData;
    typedef boost::shared_ptr<SysExData> SysExPtr;

    struct null_deleter {
        void operator()(void const *) const {}
    };


    MidiEvent()
      : type(MIDI_EVENT_NONE)
      , port(0)
      , channel(0)
      , data1(0)
      , data2(0)
      , sysex()
      , frame(0)
    {
    }

    MidiEvent(MidiEventType type_, int port_, int channel_, int data1_, int data2_)
      : type(type_)
      , port(port_)
      , channel(channel_)
      , data1(data1_)
      , data2(data2_)
      , sysex()
      , frame(0)
    {
    }

    SysExData get_sysex_data() const {
        return *sysex;
    }

    void set_sysex_data(SysExData const & sysex_) {
        sysex.reset(new SysExData(sysex_));
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

    SysExPtr sysex;

    uint64_t frame;
};


inline bool operator==(MidiEvent const & lhs, MidiEvent const & rhs)
{
    return (
        lhs.type == rhs.type &&
        lhs.port == rhs.port &&
        lhs.channel == rhs.channel &&
        lhs.data1 == rhs.data1 &&
        lhs.data2 == rhs.data2 &&
        ((!lhs.sysex && !rhs.sysex) || (lhs.sysex && rhs.sysex && *lhs.sysex == *rhs.sysex)) &&
        lhs.frame == rhs.frame
    );
}


} // Mididings


#endif // MIDIDINGS_MIDI_EVENT_HH
