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

#ifndef _UNITS_FILTERS_HH
#define _UNITS_FILTERS_HH

#include "units_base.hh"

#include <vector>
#include <string>
#include <algorithm>


class PortFilter
  : public Filter
{
  public:
    PortFilter(std::vector<int> const & ports)
      : Filter()
      , _ports(ports)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
        return (std::find(_ports.begin(), _ports.end(), ev.port) != _ports.end());
    }

  private:
    std::vector<int> _ports;
};


class ChannelFilter
  : public Filter
{
  public:
    ChannelFilter(std::vector<int> const & channels)
      : Filter()
      , _channels(channels)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
        return (std::find(_channels.begin(), _channels.end(), ev.channel) != _channels.end());
    }

  private:
    std::vector<int> _channels;
};


class KeyFilter
  : public Filter
{
  public:
    KeyFilter(int lower, int upper)
      : Filter(MIDI_EVENT_NOTEON | MIDI_EVENT_NOTEOFF, true)
      , _lower(lower)
      , _upper(upper)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
        return ((ev.note.note >= _lower || _lower == 0) &&
                (ev.note.note < _upper  || _upper == 0));
    }

  private:
    int _lower, _upper;
};


class VelocityFilter
  : public Filter
{
  public:
    VelocityFilter(int lower, int upper)
      : Filter(MIDI_EVENT_NOTEON, true)
      , _lower(lower)
      , _upper(upper)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
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
      : Filter(MIDI_EVENT_CTRL, false)
      , _ctrls(ctrls)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
        return (std::find(_ctrls.begin(), _ctrls.end(), ev.ctrl.param) != _ctrls.end());
    }

  private:
    std::vector<int> _ctrls;
};


class CtrlValueFilter
  : public Filter
{
  public:
    CtrlValueFilter(int lower, int upper)
      : Filter(MIDI_EVENT_CTRL, false)
      , _lower(lower)
      , _upper(upper)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
        return ((ev.ctrl.value >= _lower && ev.ctrl.value < _upper) || (ev.ctrl.value == _lower && !_upper));
    }

  private:
    int _lower, _upper;
};


class ProgramFilter
  : public Filter
{
  public:
    ProgramFilter(std::vector<int> const & progs)
      : Filter(MIDI_EVENT_PROGRAM, false)
      , _progs(progs)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
        return (std::find(_progs.begin(), _progs.end(), ev.ctrl.value) != _progs.end());
    }

  private:
    std::vector<int> _progs;
};


class SysExFilter
  : public Filter
{
  public:
    SysExFilter(std::string const & sysex, bool partial)
      : Filter(MIDI_EVENT_SYSEX, false)
      , _sysex(sysex)
      , _partial(partial)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
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
