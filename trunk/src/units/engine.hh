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

#ifndef MIDIDINGS_UNITS_ENGINE_HH
#define MIDIDINGS_UNITS_ENGINE_HH

#include "units/base.hh"
#include "units/util.hh"
#include "engine.hh"
#include "patch.hh"


namespace Mididings {
namespace Units {


class Sanitize
  : public UnitExImpl<Sanitize>
{
  public:
    Sanitize() { }

    template <typename B>
    typename B::Range process(B & buffer, typename B::Iterator it) const
    {
        Engine & engine = buffer.engine();

        if (engine.sanitize_event(*it)) {
            return Patch::keep_event(buffer, it);
        } else {
            return Patch::delete_event(buffer, it);
        }
    }
};


class SceneSwitch
  : public UnitExImpl<SceneSwitch>
{
  public:
    SceneSwitch(int num, int offset)
      : _num(num)
      , _offset(offset)
    { }

    template <typename B>
    typename B::Range process(B & buffer, typename B::Iterator it) const
    {
        Engine & engine = buffer.engine();

        if (_offset == 0) {
            engine.switch_scene(get_parameter(_num, *it));
        } else {
            // FIXME: handle gaps in scene numbers
            int n = engine.current_scene() + _offset;
            if (engine.has_scene(n)) {
                engine.switch_scene(n);
            }
        }

        return Patch::delete_event(buffer, it);
    }

  private:
    int const _num;
    int const _offset;
};


class SubSceneSwitch
  : public UnitExImpl<SubSceneSwitch>
{
  public:
    SubSceneSwitch(int num, int offset, bool wrap)
      : _num(num)
      , _offset(offset)
      , _wrap(wrap)
    { }

    template <typename B>
    typename B::Range process(B & buffer, typename B::Iterator it) const
    {
        Engine & engine = buffer.engine();

        if (_offset == 0) {
            engine.switch_scene(-1, get_parameter(_num, *it));
        } else {
            int n = engine.current_subscene() + _offset;
            if (_wrap) {
                n %= engine.num_subscenes();
            }
            if (engine.has_subscene(n)) {
                engine.switch_scene(-1, n);
            }
        }
        return Patch::delete_event(buffer, it);
    }

  private:
    int const _num;
    int const _offset;
    bool const _wrap;
};


} // Units
} // Mididings


#endif // MIDIDINGS_UNITS_ENGINE_HH
