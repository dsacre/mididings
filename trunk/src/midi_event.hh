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

#ifndef MIDIDINGS_MIDI_EVENT_HH
#define MIDIDINGS_MIDI_EVENT_HH

#include <vector>
#include <stdexcept>

#include <boost/cstdint.hpp>
#include <boost/shared_ptr.hpp>

#include "util/counted_objects.hh"


namespace Mididings {


enum MidiEventTypeEnum
{
    MIDI_EVENT_NONE             = 0,
    MIDI_EVENT_NOTEON           = 1 << 0,
    MIDI_EVENT_NOTEOFF          = 1 << 1,
    MIDI_EVENT_NOTE             = MIDI_EVENT_NOTEON | MIDI_EVENT_NOTEOFF,
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
    MIDI_EVENT_SYSCM            = MIDI_EVENT_SYSCM_QFRAME | MIDI_EVENT_SYSCM_SONGPOS |
                                  MIDI_EVENT_SYSCM_SONGSEL | MIDI_EVENT_SYSCM_TUNEREQ,
    MIDI_EVENT_SYSRT_CLOCK      = 1 << 12,
    MIDI_EVENT_SYSRT_START      = 1 << 13,
    MIDI_EVENT_SYSRT_CONTINUE   = 1 << 14,
    MIDI_EVENT_SYSRT_STOP       = 1 << 15,
    MIDI_EVENT_SYSRT_SENSING    = 1 << 16,
    MIDI_EVENT_SYSRT_RESET      = 1 << 17,
    MIDI_EVENT_SYSRT            = MIDI_EVENT_SYSRT_CLOCK | MIDI_EVENT_SYSRT_START |
                                  MIDI_EVENT_SYSRT_CONTINUE | MIDI_EVENT_SYSRT_STOP |
                                  MIDI_EVENT_SYSRT_SENSING | MIDI_EVENT_SYSRT_RESET,
    MIDI_EVENT_SYSTEM           = MIDI_EVENT_SYSEX | MIDI_EVENT_SYSCM | MIDI_EVENT_SYSRT,
    MIDI_EVENT_DUMMY            = 1 << 29,
    MIDI_EVENT_ANY              = (1 << 30) - 1,
};

typedef unsigned int MidiEventType;



class SysExData
  : public std::vector<unsigned char>
  , das::counted_objects<SysExData>
{
  public:
    SysExData()
      : std::vector<unsigned char>()
    { }

    SysExData(std::size_t n)
      : std::vector<unsigned char>(n)
    { }

    template <typename InputIterator>
    SysExData(InputIterator first, InputIterator last)
      : std::vector<unsigned char>(first, last)
    { }

    SysExData(SysExData const & other)
      : std::vector<unsigned char>(other)
    { }

    ~SysExData() { }

    SysExData & operator=(SysExData const & other) {
        std::vector<unsigned char>::operator=(other);
        return *this;
    }
};

typedef boost::shared_ptr<SysExData> SysExDataPtr;
typedef boost::shared_ptr<SysExData const> SysExDataConstPtr;



struct MidiEvent
  : das::counted_objects<MidiEvent>
{
    MidiEvent()
      : type(MIDI_EVENT_NONE)
      , port(0)
      , channel(0)
      , data1(0)
      , data2(0)
      , sysex()
      , frame(0)
    { }

    MidiEvent(MidiEvent const & other)
      : type(other.type)
      , port(other.port)
      , channel(other.channel)
      , data1(other.data1)
      , data2(other.data2)
      , sysex(other.sysex)
      , frame(other.frame)
    { }

    ~MidiEvent() { }

    MidiEvent & operator=(MidiEvent const & other) {
        type = other.type;
        port = other.port;
        channel = other.channel;
        data1 = other.data1;
        data2 = other.data2;
        sysex = other.sysex;
        frame = other.frame;
        return *this;
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

    SysExDataConstPtr sysex;

    uint64_t frame;
};


inline bool operator==(MidiEvent const & lhs, MidiEvent const & rhs)
{
    // the obvious case: events of different types are never equal
    if (lhs.type != rhs.type) {
        return false;
    }

    // check which fields are relevant for the given event type
    bool channel = !(lhs.type & (MIDI_EVENT_SYSTEM | MIDI_EVENT_DUMMY));
    bool data1 = (lhs.type & (MIDI_EVENT_NOTE | MIDI_EVENT_CTRL | MIDI_EVENT_POLY_AFTERTOUCH |
                              MIDI_EVENT_SYSCM_QFRAME | MIDI_EVENT_SYSCM_SONGPOS | MIDI_EVENT_SYSCM_SONGSEL));
    bool data2 = (lhs.type & (MIDI_EVENT_NOTE | MIDI_EVENT_CTRL | MIDI_EVENT_PITCHBEND |
                              MIDI_EVENT_AFTERTOUCH | MIDI_EVENT_POLY_AFTERTOUCH | MIDI_EVENT_PROGRAM |
                              MIDI_EVENT_SYSCM_SONGPOS));
    bool sysex = (lhs.type & MIDI_EVENT_SYSEX);

    // return true if each field is either irrelevant or identical
    return (
        lhs.port == rhs.port &&
        (!channel || lhs.channel == rhs.channel) &&
        (!data1 || lhs.data1 == rhs.data1) &&
        (!data2 || lhs.data2 == rhs.data2) &&
        (!sysex || (lhs.sysex && rhs.sysex && *lhs.sysex == *rhs.sysex)) &&
        lhs.frame == rhs.frame
    );
}

inline bool operator!=(MidiEvent const & lhs, MidiEvent const & rhs)
{
    return !(lhs == rhs);
}


} // Mididings


#endif // MIDIDINGS_MIDI_EVENT_HH
