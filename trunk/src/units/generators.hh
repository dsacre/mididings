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

#ifndef MIDIDINGS_UNITS_GENERATORS_HH
#define MIDIDINGS_UNITS_GENERATORS_HH

#include "units/base.hh"
#include "units/util.hh"


namespace Mididings {
namespace Units {


class Generator
  : public Unit
{
  public:
    Generator(MidiEventType type, int port, int channel, int data1, int data2)
      : _type(type)
      , _port(port)
      , _channel(channel)
      , _data1(data1)
      , _data2(data2)
    { }

    virtual bool process(MidiEvent & ev) const
    {
        MidiEvent ev_new(ev);

        ev_new.type = _type;
        ev_new.port = get_parameter(_port, ev);
        ev_new.channel = get_parameter(_channel, ev);
        ev_new.data1 = get_parameter(_data1, ev);
        ev_new.data2 = get_parameter(_data2, ev);

        ev = ev_new;

        return true;
    }

  private:
    MidiEventType const _type;
    int const _port;
    int const _channel;
    int const _data1;
    int const _data2;
};


class SysExGenerator
  : public Unit
{
  public:
    SysExGenerator(int port, SysExDataConstPtr const & sysex)
      : _port(port)
      , _sysex(sysex)
    { }

    virtual bool process(MidiEvent & ev) const
    {
        ev.type = MIDI_EVENT_SYSEX;
        ev.port = get_parameter(_port, ev);
        ev.channel = 0;
        ev.data1 = 0;
        ev.data2 = 0;
        ev.sysex = _sysex;

        return true;
    }

  private:
    int const _port;
    SysExDataConstPtr const _sysex;
};


} // Units
} // Mididings


#endif // MIDIDINGS_UNITS_GENERATORS_HH
