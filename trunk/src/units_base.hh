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

#ifndef _UNITS_BASE_HH
#define _UNITS_BASE_HH

#include "midi_event.hh"
#include "patch.hh"
#include "units_util.hh"

#include <boost/shared_ptr.hpp>

#include "util/debug.hh"


class Unit
{
  public:
    Unit()
    {
        DEBUG_FN();
    }

    virtual ~Unit()
    {
        DEBUG_FN();
    }

    virtual bool process(MidiEvent & ev) = 0;
};


class UnitEx
{
  public:
    UnitEx()
    {
        DEBUG_FN();
    }

    virtual ~UnitEx()
    {
        DEBUG_FN();
    }

    virtual Patch::EventRange process(Patch::Events & buf, Patch::EventIter it) = 0;
};


class Filter
  : public Unit
{
  public:
    Filter(MidiEventTypes types)
      : _types(types)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        return match_type(ev);
    }

    MidiEventTypes types() const
    {
        return _types;
    }

  protected:
    bool match_type(MidiEvent & ev)
    {
        return (ev.type & _types);
    }

  private:
    MidiEventTypes const _types;
};


class InvertedFilter
  : public Filter
{
  public:
    InvertedFilter(boost::shared_ptr<Filter> filter, bool ignore_types)
      : Filter(MIDI_EVENT_ANY)
      , _filter(filter)
      , _ignore_types(ignore_types)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (_ignore_types) {
            return !_filter->process(ev);
        } else {
            return !(_filter->types() & ev.type) || !_filter->process(ev);
        }
    }

  private:
    boost::shared_ptr<Filter> _filter;
    bool _ignore_types;
};


class Pass
  : public Unit
{
  public:
    Pass(bool pass)
      : _pass(pass)
    {
    }

    virtual bool process(MidiEvent & /*ev*/)
    {
        return _pass;
    }

  private:
    bool _pass;
};


#endif // _UNITS_BASE_HH
