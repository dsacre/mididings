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
    SceneSwitch(int num)
      : _num(num)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        TheEngine->switch_scene(get_parameter(_num, ev));
        return false;
    }

  private:
    int _num;
};


#endif // _UNITS_ENGINE_HH
