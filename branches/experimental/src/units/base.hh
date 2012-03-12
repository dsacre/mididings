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

#ifndef MIDIDINGS_UNITS_BASE_HH
#define MIDIDINGS_UNITS_BASE_HH

#include "midi_event.hh"
#include "patch.hh"
#include "units/util.hh"

#include <boost/shared_ptr.hpp>

#include "util/debug.hh"


namespace Mididings {
namespace Units {


class Unit
{
  public:
    Unit()
    {
    }

    virtual ~Unit()
    {
    }

    virtual bool process(MidiEvent & ev) = 0;
};


class UnitEx
{
  public:
    UnitEx()
    {
    }

    virtual ~UnitEx()
    {
    }

    virtual Patch::EventRange process(Patch::Events & buf, Patch::EventIter it) = 0;
};


class Filter
  : public Unit
{
    friend class InvertedFilter;

  public:
    Filter()
      : _types(MIDI_EVENT_ANY)
      , _pass_other(false)
    {
    }

    Filter(MidiEventTypes types, bool pass_other)
      : _types(types)
      , _pass_other(pass_other)
    {
    }

  protected:
    virtual bool process(MidiEvent & ev)
    {
        if (ev.type & types()) {
            return process_filter(ev);
        } else {
            return pass_other();
        }
    }

    virtual bool process_filter(MidiEvent & ev) = 0;

    MidiEventTypes types() const
    {
        return _types;
    }

    bool pass_other() const
    {
        return _pass_other;
    }

  private:
    MidiEventTypes _types;
    bool _pass_other;
};


class InvertedFilter
  : public Filter
{
  public:
    InvertedFilter(boost::shared_ptr<Filter> filter, bool negate)
      : Filter()
      , _filter(filter)
      , _negate(negate)
    {
    }

    virtual bool process_filter(MidiEvent & ev)
    {
        if (_negate) {
            return !_filter->process(ev);
        } else {
            if (ev.type & _filter->types()) {
                return !_filter->process_filter(ev);
            } else {
                return _filter->pass_other();
            }
        }
    }

  private:
    boost::shared_ptr<Filter> _filter;
    bool _negate;
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


} // Units
} // Mididings


#endif // MIDIDINGS_UNITS_BASE_HH
