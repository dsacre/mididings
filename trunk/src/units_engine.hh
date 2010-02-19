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

#ifndef _UNITS_ENGINE_HH
#define _UNITS_ENGINE_HH

#include "units_base.hh"
#include "units_util.hh"
#include "engine.hh"


class Sanitize
  : public Unit
{
  public:
    Sanitize()
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        return TheEngine->sanitize_event(ev);
    }
};


class SceneSwitch
  : public Unit
{
  public:
    SceneSwitch(int num, int offset)
      : _num(num)
      , _offset(offset)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (_offset == 0) {
            TheEngine->switch_scene(get_parameter(_num, ev));
        } else {
            int n = TheEngine->current_scene() + _offset;
            if (TheEngine->has_scene(n)) {
                TheEngine->switch_scene(n);
            }
        }
        return false;
    }

  private:
    int _num;
    int _offset;
};


#endif // _UNITS_ENGINE_HH
