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
    friend class InvertedFilter;

  public:
    Filter()
      : _handled_types(MIDI_EVENT_ANY)
      , _pass_other(false)
    {
    }

    Filter(MidiEventTypes handled_types, bool pass_other)
      : _handled_types(handled_types)
      , _pass_other(pass_other)
    {
    }

  protected:
    virtual bool process(MidiEvent & ev)
    {
        if (ev.type & handled_types()) {
            return process_filter(ev);
        } else {
            return pass_other();
        }
    }

    virtual bool process_filter(MidiEvent & ev) = 0;

    MidiEventTypes handled_types() const
    {
        return _handled_types;
    }

    bool pass_other() const
    {
        return _pass_other;
    }

  private:
    MidiEventTypes _handled_types;
    bool _pass_other;
};


class InvertedFilter
  : public Filter
{
  public:
    InvertedFilter(boost::shared_ptr<Filter> filter, bool ignore_types)
      : Filter()
      , _filter(filter)
      , _ignore_types(ignore_types)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
        if (_ignore_types) {
            return !_filter->process(ev);
        } else {
            if (ev.type & _filter->handled_types()) {
                return !_filter->process_filter(ev);
            } else {
                return _filter->pass_other();
            }
        }
    }

  private:
    boost::shared_ptr<Filter> _filter;
    bool _ignore_types;
};


class TypeFilter
  : public Filter
{
  public:
    TypeFilter(MidiEventTypes types)
      : Filter()
      , _types(types)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
        return (ev.type & _types);
    }

    MidiEventTypes _types;
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
