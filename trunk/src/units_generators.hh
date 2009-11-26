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

#ifndef _UNITS_GENERATORS_HH
#define _UNITS_GENERATORS_HH

#include "units_base.hh"
#include "units_util.hh"

#include <string>


class GenerateEvent
  : public Unit
{
  public:
    GenerateEvent(int type, int port, int channel, int data1, int data2)
      : _type((MidiEventType)type)
      , _port(port)
      , _channel(channel)
      , _data1(data1)
      , _data2(data2)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        MidiEvent ev_new;

        ev_new.type = _type;
        ev_new.port = get_parameter(_port, ev);
        ev_new.channel = get_parameter(_channel, ev);
        ev_new.data1 = get_parameter(_data1, ev);
        ev_new.data2 = get_parameter(_data2, ev);
        ev_new.frame = ev.frame;

        ev = ev_new;

        return true;
    }

  private:
    MidiEventType _type;
    int _port;
    int _channel;
    int _data1;
    int _data2;
};


class GenerateSysEx
  : public Unit
{
  public:
    GenerateSysEx(int port, std::string const & sysex)
      : _port(port)
      , _sysex(sysex)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        ev.type = MIDI_EVENT_SYSEX;
        ev.port = get_parameter(_port, ev);
        ev.channel = 0;
        ev.data1 = 0;
        ev.data2 = 0;
        ev.sysex.reset(&_sysex, MidiEvent::null_deleter());

        return true;
    }

  private:
    int _port;
    std::string _sysex;
};


#endif // _UNITS_GENERATORS_HH
