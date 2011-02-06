/*
 * mididings
 *
 * Copyright (C) 2008-2011  Dominic Sacré  <dominic.sacre@gmx.de>
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
      : _types(MIDI_EVENT_ANY)
    {
    }

    Filter(MidiEventTypes types)
      : _types(types)
    {
    }

  protected:
    virtual bool process(MidiEvent & ev)
    {
        if (ev.type & types()) {
            return process_filter(ev);
        } else {
            return true;
        }
    }

    virtual bool process_filter(MidiEvent & ev) = 0;

    MidiEventTypes types() const
    {
        return _types;
    }

  private:
    MidiEventTypes _types;
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
                return true;
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
