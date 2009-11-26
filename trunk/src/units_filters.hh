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

#ifndef _UNITS_FILTERS_HH
#define _UNITS_FILTERS_HH

#include "units_base.hh"

#include <vector>
#include <string>


class PortFilter
  : public Filter
{
  public:
    PortFilter(std::vector<int> const & ports)
      : Filter(MIDI_EVENT_ANY)
      , _ports(ports)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        for (std::vector<int>::iterator i = _ports.begin(); i != _ports.end(); ++i) {
            if (ev.port == *i) return true;
        }
        return false;
    }

  private:
    std::vector<int> _ports;
};


class ChannelFilter
  : public Filter
{
  public:
    ChannelFilter(std::vector<int> const & channels)
      : Filter(MIDI_EVENT_ANY)
      , _channels(channels)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        for (std::vector<int>::iterator i = _channels.begin(); i != _channels.end(); ++i) {
            if (ev.channel == *i) return true;
        }
        return false;
    }

  private:
    std::vector<int> _channels;
};


class KeyFilter
  : public Filter
{
  public:
    KeyFilter(int lower, int upper)
      : Filter(MIDI_EVENT_NOTEON | MIDI_EVENT_NOTEOFF)
      , _lower(lower)
      , _upper(upper)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (!match_type(ev)) return true;
        return ((ev.note.note == _lower && _upper == 0) ||
                (ev.note.note >= _lower && ev.note.note < _upper));
    }

  private:
    int _lower, _upper;
};


class VelocityFilter
  : public Filter
{
  public:
    VelocityFilter(int lower, int upper)
      : Filter(MIDI_EVENT_NOTEON)
      , _lower(lower)
      , _upper(upper)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (!match_type(ev)) return true;
        return ((ev.note.velocity >= _lower || _lower == 0) &&
                (ev.note.velocity < _upper || _upper == 0));
    }

  private:
    int _lower, _upper;
};


class CtrlFilter
  : public Filter
{
  public:
    CtrlFilter(std::vector<int> const & ctrls)
      : Filter(MIDI_EVENT_CTRL)
      , _ctrls(ctrls)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (!match_type(ev)) return true;
        for (std::vector<int>::iterator i = _ctrls.begin(); i != _ctrls.end(); ++i) {
            if (ev.ctrl.param == *i) return true;
        }
        return false;
    }

  private:
    std::vector<int> _ctrls;
};


class CtrlValueFilter
  : public Filter
{
  public:
    CtrlValueFilter(int lower, int upper)
      : Filter(MIDI_EVENT_CTRL)
      , _lower(lower)
      , _upper(upper)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (!match_type(ev)) return true;
        return ((ev.ctrl.value >= _lower && ev.ctrl.value < _upper) || (ev.ctrl.value == _lower && !_upper));
    }

  private:
    int _lower, _upper;
};


class ProgFilter
  : public Filter
{
  public:
    ProgFilter(std::vector<int> const & progs)
      : Filter(MIDI_EVENT_PROGRAM)
      , _progs(progs)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (!match_type(ev)) return true;
        for (std::vector<int>::iterator i = _progs.begin(); i != _progs.end(); ++i) {
            if (ev.ctrl.value == *i) return true;
        }
        return false;
    }

  private:
    std::vector<int> _progs;
};


class SysExFilter
  : public Filter
{
  public:
    SysExFilter(std::string const & sysex, bool partial)
      : Filter(MIDI_EVENT_SYSEX)
      , _sysex(sysex)
      , _partial(partial)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (!match_type(ev)) return true;
        if (_partial) {
            return ev.sysex->find(_sysex) == 0;
        } else {
            return *ev.sysex == _sysex;
        }
    }

    std::string _sysex;
    bool _partial;
};


#endif // _UNITS_FILTERS_HH
