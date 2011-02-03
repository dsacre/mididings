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

#ifndef MIDIDINGS_UNITS_ENGINE_HH
#define MIDIDINGS_UNITS_ENGINE_HH

#include "units/base.hh"
#include "units/util.hh"
#include "engine.hh"


namespace Mididings {
namespace Units {


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
            // FIXME: handle gaps in scene numbers
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


class SubSceneSwitch
  : public Unit
{
  public:
    SubSceneSwitch(int num, int offset, bool wrap)
      : _num(num)
      , _offset(offset)
      , _wrap(wrap)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (_offset == 0) {
            TheEngine->switch_scene(-1, get_parameter(_num, ev));
        } else {
            int n = TheEngine->current_subscene() + _offset;
            if (_wrap) {
                n %= TheEngine->num_subscenes();
            }
            if (TheEngine->has_subscene(n)) {
                TheEngine->switch_scene(-1, n);
            }
        }
        return false;
    }

  private:
    int _num;
    int _offset;
    bool _wrap;
};


} // Units
} // Mididings


#endif // MIDIDINGS_UNITS_ENGINE_HH
